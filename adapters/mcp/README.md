# MCP adapter

Projects one canonical skill (`skill.yaml` + `SKILL.md` + resources) onto the
**Model Context Protocol's in-flight Skills Extension (SEP-2640)**. Implemented
in [`adapter.py`](./adapter.py).

**Read this before the other five adapter READMEs, not after.** Every other
target in this library (Claude Code, Cursor, Codex, Windsurf/Devin,
Antigravity) is a real, shipping, file-based convention that a live coding
agent reads today. MCP is not: "Skills over MCP" is an **Extensions Track**
SEP — Accepted by MCP's Core Maintainers on 2026-09-03, six days before the
research this adapter is built from — with **no reference implementation and
no conformance tests yet** ([research/agent-ecosystems/mcp.md](../../research/agent-ecosystems/mcp.md)
§1). This adapter is a bet on a documented shape holding steady between
"Accepted" and "actually implemented," not a translation into a format any
running MCP server or client currently speaks. Treat everything below as
**speculative and forward-looking**, and re-verify against the ratified
extension and a real reference implementation before using this adapter for
anything that matters.

## 1. Supported capabilities

MCP resources natively carry two of the canonical skill's fields, per
SEP-2640's reuse of the `Resource` object's own `name`/`description` fields
([mcp.md](../../research/agent-ecosystems/mcp.md) §1; [adapter-projection.md](../../core/skill-specification/adapter-projection.md)
field-mapping matrix, MCP column):

| Canonical field | MCP representation |
|---|---|
| `name` | resource `name` |
| `description` | resource `description` |
| body (Markdown) | the `SKILL.md` resource's text content, read via `resources/read` |

That's the entire native surface. Everything else the canonical spec defines —
activation conditions, capability requirements, execution tier, arguments,
governance metadata — has no dedicated slot in a `Resource` object and is
handled per the Lossiness contract (`body` note or `drop+note`; see
[`adapter.py`](./adapter.py) `project()`).

## 2. Limitations

### `required_capabilities` and `execution_tier`: out of scope for a single skill's resource, not just unsupported

These two fields are dropped from every other adapter's frontmatter too in
some form, but MCP is the one target where the reason is **structural, not a
missing feature that a future SEP revision could plausibly add to a
resource**:

- **`required_capabilities`** — under MCP, "what tools/capabilities does this
  functionality need" is answered by a **server's own tool declaration**
  (`tools/list`, capability negotiation via `capabilities.tools` /
  `capabilities.extensions` — [mcp.md](../../research/agent-ecosystems/mcp.md)
  §4, §10.3, §12), not by metadata attached to one resource among possibly
  many the server exposes. A resource is a URI-addressed blob of content; it
  does not participate in MCP's capability-negotiation handshake at all. The
  MCP *server* hosting `skill://code-review/SKILL.md` might separately expose
  a `run_security_scan` tool the skill's body tells the agent to call — but
  that tool's existence and schema are declared once, server-wide, in
  `tools/list`, completely independent of any one resource's metadata. There
  is no field on a `Resource` object SEP-2640 could add that would express
  "this skill needs tool X" in a way an MCP client would enforce before
  serving the resource.
- **`execution_tier`** — MCP resources have no isolation, sandboxing, or
  fork/subagent concept of their own (unlike, say, Claude Code's
  `context: fork` or Windsurf's subagent Preview). A resource is inert content
  the client reads; whatever executes as a result of reading it (if anything)
  is entirely the requesting agent's own runtime concern, orthogonal to the
  resource-fetch itself. The projection matrix in
  [adapter-projection.md](../../core/skill-specification/adapter-projection.md)
  correctly marks this cell `n/a`, not `body` or `drop+note` — there is no
  MCP-side artifact this could even degrade into.

The adapter reflects this by dropping both fields with a note pointing at the
serving server's tool manifest and the projection matrix, respectively (see
[`adapter.py`](./adapter.py) lines 44–52), rather than pushing them into the
resource body the way `activation_conditions` is pushed. Pushing them into
the body would misrepresent them as advisory prose when the real analog (a
server-side tool declaration) is a protocol-level construct that lives
somewhere else entirely — doing so would blur a structural distinction this
README exists to keep sharp.

### Everything else that's out of scope

- **No activation semantics.** `activation_mode`/`activation_conditions` have
  no MCP-native trigger concept — MCP resources are fetched when a client
  decides to fetch them (`resources/read`), which the spec explicitly leaves
  "application-driven" ([mcp.md](../../research/agent-ecosystems/mcp.md) §3).
  The adapter keeps this guidance as a body note; nothing enforces it.
- **No arguments/inputs schema for resources.** Canonical `inputs` map more
  naturally to MCP *Tools'* `inputSchema` or *Prompts'* `arguments`, not
  Resources — SEP-2640 targets skills as resources, so this adapter does not
  attempt an inputs projection.
- **Governance-only fields** (`source_references`, `evaluation_criteria`,
  `depends_on_skills`, `failure_handling`, `escalation`, etc.) are dropped
  from the emitted artifacts with a manifest note, same as every other
  target, per Lossiness contract L-3 — canonical source stays `skill.yaml`.

## 3. Packaging format — the resource-URI model

SEP-2640 represents a skill as a **resource**, not a file at a path
([mcp.md](../../research/agent-ecosystems/mcp.md) §1):

- Primary content lives at `skill://<slug>/SKILL.md` — a URI, fetched via
  `resources/read`, not a filesystem path.
- Discovery happens through a separate, **aggregate** resource,
  `skill://index.json`, that lists every skill an MCP server exposes.

This adapter deliberately does **not** build `skill://index.json` itself.
`project(skill)` takes one `Skill` and returns one skill's resource body plus
that one skill's own **index-entry fragment** — the JSON object that would
become one element of the aggregate index's list — and stops there
([`adapter.py`](./adapter.py) lines 57–68):

```python
return {uri: body, f"{uri}.index-entry.json": index_entry}, manifest
```

This is the correct boundary, not a missing feature. Every adapter in this
library is a pure function of **one canonical skill in, one target artifact
set out** — that contract is what makes each adapter callable independently,
testable independently, and composable by whatever drives them (a build
script iterating over `skills/*/`). `skill://index.json` is inherently
cross-skill: it doesn't exist until every skill's fragment has been produced.
Building it inside this adapter would mean either (a) requiring the whole
skill library as input to a "single skill" projection, breaking the one-call/
one-skill contract every other target adapter honors, or (b) having the
adapter maintain hidden cross-call state to accumulate fragments, which none
of the other five adapters do or need to. Aggregating fragments into one
`skill://index.json` belongs to whatever caller iterates over the full skill
set — the same place that would, for a file-based target, walk `skills/*/`
and write each skill to its own directory. The adapter's job ends at
producing the one fragment; assembly is the caller's.

### Worked example

Running the adapter against `skills/code-review/` (id `SK-CONV-007`) via:

```python
from lib.skill_loader import load
from mcp.adapter import project

skill = load("skills/code-review")
artifacts, manifest = project(skill)
```

produces two artifacts, keyed by URI:

**`skill://code-review/SKILL.md`** — the resource body. This is the skill's
Markdown body (Purpose & scope, When to use, Knowledge, Decision framework,
Workflow, …) with two appended body notes the adapter always adds for MCP —
an "Activation guidance" note (since `activation_conditions` has no native
slot) and a "Capability requirements" note (since `required_capabilities` has
no native slot). Truncated:

```markdown
## Purpose & scope

Review a diff/PR/changeset for correctness, quality, security, and
convention adherence, aggregating findings into ranked, actionable output.
...

## Activation guidance (library-defined, not natively enforced here)

- A change is up for review
- The user asks for a code review
- A pre-merge gate is in play
- NOT: Authoring net-new code (the build skills own that, though they may self-check)
- NOT: No change exists to review

## Capability requirements (enforced by SK-ORCH-002 at runtime, not this file)

- No special capabilities required.
```

**`skill://code-review/SKILL.md.index-entry.json`** — this one skill's
fragment for the aggregate index, in full:

```json
{
  "uri": "skill://code-review/SKILL.md",
  "name": "Code review",
  "description": "Review a change for correctness, quality, security, and convention adherence — find correctness bugs directly, delegate security/perf findings to their domain skills, check comment and code-quality convention adherence, rank findings by severity, and distinguish confirmed from speculative issues. Use when a change is up for review, the user asks for a review, or as a pre-merge gate. Not for authoring net-new code."
}
```

A caller aggregating the whole library would collect one such fragment per
skill and assemble:

```json
{ "skills": [ { "uri": "skill://code-review/SKILL.md", ... }, { "uri": "skill://backend-architecture/SKILL.md", ... }, ... ] }
```

into the single `skill://index.json` a real MCP server would serve.

The accompanying loss manifest for this same run (`skill_id: SK-CONV-007`,
`target: mcp`) records `name`/`description` as `native`, `activation_conditions`
as `body`, `required_capabilities` and `execution_tier` as `drop+note` with
the distinctions from §2 above, and every governance-only field
(`source_references`, `evaluation_criteria`, `depends_on_skills`,
`failure_handling`, `escalation`, `skill_version`, `spec_version`, etc.) as
`drop+note` pointing back to `skill.yaml`.

## 4. Loading behavior

Per the secondary sources cited in the research doc ([mcp.md](../../research/agent-ecosystems/mcp.md)
§1), an MCP client discovering skills exposed this way would:

1. Call a `skills/list` (or the standard `resources/list`, since Skills is
   built on the Resources primitive, not a new primitive) to enumerate what a
   server exposes — or fetch `skill://index.json` directly as the discovery
   resource.
2. Call `skills/get` (or `resources/read` against a specific `skill://<slug>/SKILL.md`
   URI) to fetch one skill's content.
3. Alternatively, some secondary sources describe a `read_skill` tool
   layered on top, giving a model a tool-call-shaped way to pull a skill's
   content into context rather than a resource-read.

All three of `skills/list`/`skills/get`/`read_skill` are described as
**layered on top of, not replacing,** the standard `resources/list` /
`resources/read` methods — consistent with SEP-2640 being an Extensions Track
SEP built on the existing Resources primitive rather than a new core
primitive. Whether a resource is auto-loaded into a model's context at all is
explicitly left to the client — MCP resources are "application-driven,"
per the base spec's own resources documentation ([mcp.md](../../research/agent-ecosystems/mcp.md)
§3) — so nothing guarantees a skill this adapter projects is actually read
by a given agent at a given moment, only that it is *fetchable* once a
server hosts it at the stated URI.

## 5. Compatibility assumptions

This adapter assumes:

- SEP-2640's documented shape (resource URIs under `skill://`, an
  `index.json` discovery resource, `name`/`description`/body metadata reused
  from `Resource`) holds steady between "Accepted by Core Maintainers" and
  whatever a reference implementation and conformance tests eventually lock
  in. Accepted SEPs can still change shape during implementation.
- A server implementing Skills-over-MCP negotiates the extension via the
  `extensions` map on `ClientCapabilities`/`ServerCapabilities`
  ([mcp.md](../../research/agent-ecosystems/mcp.md) §12) — meaning a client
  that doesn't opt in simply never sees these resources at all, extensions
  being "always disabled by default" per the framework's own rules. This
  adapter's output is inert on any MCP client/server pair that hasn't
  explicitly turned Skills-over-MCP on.
- The coordinating **Agent Skills** content format (agentskills.io) — the
  same `SKILL.md` convention this whole library is built on — is what
  SEP-2640 intends the resource body to carry, so the canonical body needs
  no reformatting to become the resource's text content. This is stated as
  the WG's coordination intent in the research, not as a locked, tested fact.
- MCP's Legacy/Modern protocol-era split ([mcp.md](../../research/agent-ecosystems/mcp.md)
  §10) doesn't change anything about this adapter's output shape, since
  Resources' basic `name`/`description`/URI/content shape is one of the
  more stable parts of the protocol across both eras — but this has not been
  tested against an actual dual-era server.

None of this is a confirmed-working integration. It is a best-effort target
built from a single, freshly-Accepted SEP and secondary-source descriptions
of its discovery methods, aimed at a moving target that had not yet produced
running code as of the research date.

## 6. Version considerations

**This is the lowest-confidence target of the six adapters in this library,
and should be treated as speculative/forward-looking until proven otherwise.**

- SEP-2640 ("Skills Extension") was **Accepted by Core Maintainers on
  2026-09-03** — per the research doc, six days before the research pass that
  grounds this adapter (2026-09-09) — and was explicitly **pre-reference-
  implementation** at that time: "moving toward reference implementations and
  conformance tests" ([mcp.md](../../research/agent-ecosystems/mcp.md) §1).
  There is no MCP server or client known to implement Skills-over-MCP that
  this adapter's output has been, or could yet be, tested against.
- The base MCP specification itself underwent "the largest revision of the
  protocol since launch" on 2026-07-28, roughly six weeks before this
  research — a near-total rewrite (removing the connection handshake,
  deprecating Roots/Sampling/Logging, introducing the Extensions framework
  that Skills-over-MCP itself depends on to exist as a concept). Most
  currently-deployed MCP clients/servers were very likely built against
  earlier "Legacy" revisions, not this one ([mcp.md](../../research/agent-ecosystems/mcp.md)
  §0). Skills-over-MCP is layered on machinery (the Extensions framework,
  SEP-2133) that is itself only weeks old.
- Extensions are "always disabled by default and require explicit opt-in
  from the developer" at every layer — SDK, server, and client
  ([mcp.md](../../research/agent-ecosystems/mcp.md) §12) — so even once a
  reference implementation exists, no MCP deployment will surface
  Skills-over-MCP resources without deliberate, explicit adoption on both
  ends of the connection.
- **Action before trusting this adapter for anything real:** re-fetch
  SEP-2640's current status, check for a shipped reference implementation in
  at least one Tier-1 SDK (TypeScript/Python/Go/C#), and re-verify the
  `skill://` URI shape, `index.json` schema, and `skills/list`/`skills/get`/
  `read_skill` method names against whatever actually shipped — all three
  are currently sourced from "secondary sources," not the ratified extension
  text itself. Do not assume this README or `adapter.py` still matches
  SEP-2640's shape without that check; re-verify against
  [core/skill-specification/adapter-projection.md](../../core/skill-specification/adapter-projection.md)'s
  own "Snapshot caveat" and the MCP-based-agents subsection first, since both
  already carry the same "provisional" flag this README repeats.
