# Cross-Ecosystem Comparison

Synthesized 2026-09-09 from the seven companion documents in this directory
(`claude-code.md`, `cursor.md`, `codex.md`, `windsurf.md`, `antigravity.md`,
`mcp.md`, `vscode.md`). Each of those documents cites its own primary
sources; this document does not re-cite every underlying URL — it
cross-references claims already sourced there. Where this document draws a
conclusion that goes beyond what any single ecosystem doc states, it is
marked `[Synthesis]`. Nothing here is a spec proposal — no skill format is
designed in this document.

**Method note**: this synthesis was done by reading all seven documents in
full, not by delegating the comparison itself — the individual research
passes were parallelized, but weighing them against each other is a single
judgment call and is kept in one place.

**A caveat that applies to the whole document**: every one of the seven
ecosystems is, per its own research doc, either mid-migration, less than
eight months old as a feature, or built on a protocol revision that is six
weeks old. Windsurf is mid-rebrand into "Devin Desktop" with two
non-interoperating agent runtimes running side by side. Cursor's Skills and
Subagents shipped 2026-01-22. Codex's docs host itself 308-redirected during
this research. MCP's current spec finalized 2026-07-28 and explicitly
documents a long **Legacy vs. Modern** mixed-transition period. Antigravity
migrated off its own prior "Workflows" mechanism in May 2026. **Nothing
below should be read as a stable target — it is a snapshot**, and a
vendor-neutral spec built against it should expect all of it to keep moving.

---

## Headline finding: a real, multi-vendor convergence on "Agent Skills"

The single strongest cross-cutting signal in all seven documents: **six of
the seven ecosystems explicitly state, in their own official docs, that
their "Skills" feature adopts an external, named open standard** —
consistently referred to as "Agent Skills" and hosted at **agentskills.io**
— rather than a proprietary format:

| Ecosystem | Explicit claim in official docs |
|---|---|
| Claude Code | "Claude Code skills follow the Agent Skills open standard, which works across multiple AI tools" |
| Cursor | "Agent Skills is an open standard for extending AI agents with specialized capabilities," cites agentskills.io |
| Codex | "build on the open agent skills standard" hosted at agentskills.io |
| Antigravity | "the open industry standard for Agent Skills" / "the cross-platform agent specification" |
| VS Code | "an open standard at agentskills.io," explicitly portable across Copilot in VS Code, Copilot CLI, and Copilot's cloud agent |
| MCP (SEP-2640) | the in-progress Skills Extension explicitly coordinates with "the external Agent Skills spec... on content format and well-known URI discovery" rather than replacing it |
| Windsurf/Devin | Has the same `SKILL.md` + frontmatter + progressive-disclosure shape, but the fetched docs did **not** explicitly cite agentskills.io by name — behaviorally identical, but not confirmed as a stated adoption |

`[Synthesis]` This is not six vendors independently inventing the same
thing — it is six vendors citing the *same external standard*. That changes
the shape of this project's task: the open question is not "should we
invent a vendor-neutral skill format" but "should `core/` adopt (or closely
track) agentskills.io rather than design a competing format from scratch."
This project has not yet directly fetched and read the agentskills.io
specification itself — every ecosystem doc's knowledge of it is secondhand,
via each vendor's *description* of adopting it. **That is the single
highest-value next research step**, and is listed as the first unresolved
question below.

Beneath that shared standard, every vendor layers its own proprietary
extensions (tool scoping, subagent execution, dynamic injection, invocation
control) — the convergence is real but partial, at the level of the base
file format and metadata fields, not the full feature surface.

---

## Dimension-by-dimension synthesis

### Skills

- **Converges on**: a directory containing a `SKILL.md` file with `name` +
  `description` YAML frontmatter and a Markdown instruction body; optional
  `scripts/`/`references/`/`assets/`-style subdirectories; **progressive
  disclosure** (only `name`+`description` loaded/indexed up front, full body
  loaded only on invocation/relevance-match) — present in all seven
  ecosystems without exception, including MCP's in-progress extension.
  Storage is scoped at (at least) project/workspace and user/global levels,
  with several vendors adding an admin/enterprise/system tier.
  Secondary convergence: `.agents/skills/` as a shared directory name
  appears as one of the recognized paths in Cursor, Codex, Antigravity, and
  VS Code (though never the *only* path any of them scans).
- **Diverges on**: everything layered on top of that minimal shape —
  invocation-control flags (`disable-model-invocation`, `user-invocable`),
  tool-scoping syntax, isolated-subagent execution (`context: fork` in
  Claude Code/VS Code, `agents/openai.yaml` in Codex, no equivalent
  documented in Cursor/Windsurf), glob-based auto-activation (`paths` in
  Claude Code/Cursor), dynamic shell injection (Claude-Code-only, as far as
  documented), cosmetic fields (Cursor's `icon`/`color`). Distribution-at-scale
  mechanisms differ completely: GitHub-link install (Cursor, Codex),
  marketplace/plugin bundles (all of them, differently shaped), enterprise
  MDM push (Windsurf, Claude Code).

### Rules / project instructions / user instructions

- **Converges on**: a project-root Markdown file (or directory of them)
  auto-loaded at session start without explicit invocation, plus a
  user/global-scope equivalent. **`AGENTS.md` specifically** is the closest
  thing to an already-standardized filename: Codex treats it as primary,
  Windsurf and VS Code auto-detect it, Cursor recognizes it as a simpler
  alternative to its own `.mdc` format, and even Claude Code — which does
  not read it natively — explicitly references it in its own docs as a
  format other tools use. A four-way activation-mode taxonomy (always-on /
  glob-scoped / model-decides-relevance / manual-only) recurs, sometimes as
  a full explicit enum (Cursor's four modes, Antigravity's four modes — near
  identical in spirit) and sometimes as a subset (Claude Code, Windsurf, VS
  Code's three-tier always-on/conditional/manual split).
- **Diverges on**: exact frontmatter field names for the same concept
  (`alwaysApply` vs. "Always On" vs. always-loaded-by-convention;
  `globs` vs. `applyTo` vs. `paths`), number of precedence tiers (2 in the
  simplest cases up to 5 for Claude Code's settings stack), merge-vs-override
  semantics (most concatenate all matching files; Cursor's Team Rules
  explicitly *override* rather than merge; Codex's file-chain concatenates
  until a byte cap is hit, then silently stops), and per-file character/line
  caps (Windsurf: 6,000/12,000 chars; Claude Code: recommends <200 lines,
  hard-skips above 4 MiB; Codex: 32 KiB total).

### Context and context loading

- **Converges on**: cheap metadata loaded eagerly, expensive content loaded
  lazily, as the general strategy for both skills and rules; some form of
  explicit-mention syntax for users to pull specific context into a turn
  (`@` in Cursor/Windsurf, `#` in VS Code); summarization/compaction once a
  session runs long (documented explicitly for Claude Code; not directly
  confirmed for the others in this pass, though plausible).
- **Diverges on** — and this is a real, verified factual split, not just
  surface syntax: **whether the agent maintains a standing embeddings/RAG
  index of the repository at all.** Cursor and Windsurf explicitly document
  a persistent semantic/vector index ("M-Query" for Windsurf, "semantic
  search" for Cursor). VS Code's index is either GitHub-server-side or a
  locally-built index depending on repo hosting. Claude Code and Codex
  explicitly do **not** appear to have one — repository understanding is
  achieved through agentic `Grep`/`Glob`/`Read`-style tool calls, not a
  pre-built index. Antigravity's mechanism is undocumented in official
  sources found. `[Synthesis]` **A vendor-neutral skill must not assume
  semantic/embedding-based repo search is available** — roughly half the
  ecosystems researched don't have it, or don't document having it.

### Tools and tool calling

- **Converges on**: a built-in tool set covering file read/write, shell
  execution, and web access; a permission/approval layer with some flavor of
  allow/ask/deny; MCP tools exposed alongside built-ins under some naming
  convention. **Multiple vendors' own docs explicitly state their
  permission/sandbox system is "best-effort" and does not cover every
  capability** — Cursor states allowlists/Run Modes are "not a security
  guarantee"; Claude Code documents that Bash argument-restriction rules are
  bypassable and recommends hooks instead; Codex documents that its sandbox
  does not cover web search, connectors, MCP, or browser tools; Antigravity
  ships the same allow/ask/deny model as a first-class SDK "Policy" object.
  `deny > ask > allow` precedence ordering is stated explicitly and
  identically by Claude Code, Antigravity, and Windsurf's newer Devin Local
  agent.
- **Diverges on**: exact tool names/verbs (no two ecosystems share a tool
  vocabulary), sandbox implementation (OS-native kernel isolation —
  Seatbelt/nsjail/bwrap — for Claude Code, Codex, and Antigravity vs.
  application-level allowlisting for Cursor and legacy Windsurf/Cascade),
  and whether a first-party "define an arbitrary custom tool" mechanism
  exists outside MCP (VS Code has its own Language Model Tools API in
  addition to MCP; Cursor and Codex route all custom tools through MCP only;
  Claude Code has a large built-in taxonomy plus MCP).

### File access and repository understanding

- **Converges on**: gitignore-style ignore-file conventions layered on top
  of (or alongside) actual `.gitignore`; some agents make `.gitignore`-matched
  files fully uneditable, not merely excluded from context (Windsurf/Devin
  states this explicitly).
- **Diverges on**: whether there's a standing index at all (see Context
  above), per-ecosystem numeric caps that are not comparable to each other
  (Windsurf's unconfirmed 10,000-file indexing cap, Claude Code's 100-file
  `Glob` cap, VS Code's 500,000-file scaling claim with no stated ceiling).

### Memory

`[Synthesis]` **This is the least standardized, most actively contested
dimension of the seven researched.** No two ecosystems agree on whether
persistent cross-session memory should exist, and one vendor is actively
removing it while another's own surfaces disagree with each other about
whether it exists:
- Claude Code: richest documented model — two channels (human-authored
  CLAUDE.md + a separate Claude-authored "auto memory" with a typed
  `user`/`feedback`/`project`/`reference` schema).
- Cursor: had a "Memories" beta (~2025); current docs no longer host a
  dedicated Memories page, and community reports describe it being
  removed/de-emphasized in the 2.x line in favor of self-directed context
  gathering — current status could not be confirmed either way.
- Codex: opt-in, per-user (not per-project) local store, explicitly and
  intentionally **not** unified with the separate ChatGPT-web/cloud memory
  system.
- Windsurf: legacy Cascade has auto-generated, per-workspace (not
  team-shared) memories; **Devin Local — the new default agent — explicitly
  does not support memories at all.** This is a live removal, happening now.
- Antigravity: "Knowledge Items," auto-distilled by a dedicated background
  subagent after every conversation — but a third-party (Mem0) vendor blog
  claims the Antigravity *CLI* specifically has no native persistent memory,
  in apparent tension with the official desktop-app documentation. Even
  within one vendor, surfaces disagree.
- MCP: no memory primitive at all, by design; entirely a
  server-implementation convention if present.
- VS Code: a three-tier (user/repo/session) memory feature exists but is
  only weakly sourced — no canonical page was found confirming its current
  details.

`[Synthesis]` **A vendor-neutral core schema should treat memory as
optional/adapter-level, never as a baseline capability a skill can assume
exists.**

### Sub-agents and delegation

- **Converges on**: a parent agent spawning a subagent with its own context
  window for a subtask, returning a result rather than raw output; a
  foreground (blocking) vs. background (async) execution split; a built-in
  "fast exploration/search" subagent type as close to universal (Claude
  Code's `Explore`, Cursor's `Explore`, Codex's `explorer`, Antigravity's
  `research`); some nesting-depth cap in every ecosystem that documents
  nesting at all (though the actual numbers vary by an order of magnitude —
  Cursor caps at one level, Claude Code at three, Antigravity at ten); and
  an explicitly documented token-cost multiplier for running subagents in
  parallel, called out independently by both Cursor and Codex.
- **Diverges on** a genuinely material design axis, not just naming:
  **whether a subagent inherits the parent conversation's history.** Claude
  Code's fork mode inherits the *entire* parent conversation verbatim.
  Antigravity's subagents explicitly do **not** inherit history (only
  safety/sandbox config). Cursor, Codex, and Windsurf's subagents start with
  fresh context. `[Synthesis]` A vendor-neutral "delegate this" primitive
  cannot assume either behavior — it needs to let the skill author declare
  which one it needs, if the target agent supports the distinction at all.

### Hooks

- **Converges on**, strikingly precisely: every ecosystem except MCP itself
  (which has no hook concept at the protocol level) implements lifecycle
  hooks as **an external process receiving JSON on stdin and communicating
  back via stdout/exit code, where exit code 2 specifically means "block
  this action."** This exact exit-code convention is documented
  independently for Claude Code, Cursor, Codex, Windsurf/Cascade,
  Antigravity, and VS Code. `[Synthesis]` This is unlikely to be six
  independent inventions of the same arbitrary number — VS Code's own docs
  confirm it ingests Claude Code's hook config directly, which strongly
  suggests one original design (plausibly Claude Code's, or a shared
  ancestor) that the rest converged around, deliberately or by copying.
  Core event categories also recur everywhere some form of them exists:
  something at session start/end, something before/after a tool call,
  something at "stop."
- **Diverges on**: the size of the event taxonomy (from Antigravity's 5
  events to Claude Code's 30+), whether hooks can only block
  (deny/allow) or can also *rewrite* the call's input, matcher syntax, and —
  critically — **fail-open vs. fail-closed default behavior on an
  unrecognized exit code.** Cursor's own docs flag this explicitly: it
  defaults fail-open (any non-2 code = allowed) unless a hook opts into
  `failClosed: true`. This is a genuine, security-relevant divergence that
  cannot be assumed to go one way. VS Code's own hook-ingestion layer is
  direct proof hooks are *not* portable as-is even between two vendors that
  both support "hooks" in the abstract: it parses Claude Code's `matcher`
  field but does not enforce it, so "all matching hooks run regardless" —
  an explicitly documented fidelity gap in the vendor doing the importing,
  not a hypothetical.

### Commands / slash commands

- **Converges on**: a Markdown file whose filename becomes a `/name`
  command; frontmatter `description`/argument-hint-style metadata;
  positional/named argument placeholder substitution (`$1`/`$ARGUMENTS`-style)
  recurring in Claude Code, Codex, and VS Code's prompt files independently.
- **A real, multi-vendor trend, not one company's idiosyncrasy**: several
  vendors are actively collapsing "commands" into "skills" as the same
  mechanism. Claude Code: "custom commands have been merged into skills."
  Codex: custom prompts are explicitly deprecated — "use skills for reusable
  instructions." Cursor ships a `/migrate-to-skills` tool that explicitly
  treats slash commands as a legacy mechanism Skills supersede. VS Code is
  the partial exception — it still keeps `.prompt.md` files distinct from
  Agent Skills, but even there, prompt files don't run on the newer "Agent
  Host" and must be converted to Skills to work there — the same collapse,
  one layer down. `[Synthesis]` **A vendor-neutral schema probably should
  not model "commands" as a primitive separate from "manually-invoked
  skills"** — the vendors themselves are actively merging that distinction
  away.

### MCP support

- **Converges on** (expected, since this is the standard itself): a
  `mcpServers`-keyed config object, a stdio-vs-remote-HTTP transport split,
  per-tool or per-server approval gating, environment-variable interpolation
  for secrets. All seven ecosystems (all six coding agents, plus VS Code)
  are MCP clients.
- **Diverges on**: config file name, location, and — in Codex's case,
  uniquely — **format**: every other ecosystem researched uses JSON for its
  MCP config; Codex uses TOML (`~/.codex/config.toml`). This divergence is
  not a documentation gap — it's confirmed by MCP's own spec (see `mcp.md`
  §13): the protocol defines the wire format once connected, but says
  nothing about how a client should be told which servers to launch, so
  every vendor invented its own file convention. Reciprocal capability (an
  agent that can *also* act as an MCP *server*) is documented only for
  Claude Code (`claude mcp serve`) and Codex (`codex mcp-server`,
  experimental) among the ecosystems researched — not universal.
  Additionally, MCP's own Legacy-vs-Modern protocol-era split (§0/§10 of
  `mcp.md`) means "supports MCP" is not even a single fact today across any
  given pair of vendors — it depends which era each side speaks.

### Configuration

- **Converges on**: a layered precedence stack with at least a
  project/workspace tier and a user/global tier; most vendors add a third,
  paid-plan-gated enterprise/managed tier above that. A recurring, important
  security behavior: **untrusted projects silently drop to a lower
  config/trust tier** in at least three ecosystems — Codex explicitly
  disables project config/AGENTS.md/skills for untrusted projects; Claude
  Code requires workspace trust before project/local-scoped MCP servers
  load; Cursor's workspace trust is off by default. This same
  "untrusted-project config degrades silently" shape recurs even though the
  exact trust UX differs per vendor.
- **Diverges on**: number of precedence tiers (2–5), merge-vs-override
  semantics per settings key, and file format — JSON is the near-universal
  choice, with Codex's TOML as the sole documented exception.

### Reusable instructions (cross-project / cross-team sharing)

- **Converges on**: a user/global-scope mirror of every project-scope
  mechanism, for one person's own cross-project reuse; and, for
  distribution beyond one person, every vendor eventually reaches for some
  kind of **bundle/plugin/marketplace** concept rather than a bare
  config-file mechanism — Claude Code plugins, Cursor's team marketplace
  plus GitHub-link install, Codex plugins/marketplace, Antigravity Plugins
  (bundling skills+agents+rules+MCP+hooks), VS Code Agent Plugins (with an
  explicit portable-core-plus-vendor-specific-extras split baked into the
  package format itself).
- **Diverges on**: whether reuse-at-scale is commercial-tier-gated (Cursor's
  Team Rules/Skill-marketplace/Team-hooks and Claude Code's managed-policy
  tier are Team/Enterprise-plan features; others are not documented as
  plan-gated), and the packaging unit's internal schema — no two "plugin"
  formats researched are compatible with each other, though VS Code's Agent
  Plugin format is explicitly *designed* to stay partly portable (a shared
  `skills/` + `mcp.json` core, with a vendor-specific extras folder) —
  arguably the most deliberate attempt at cross-vendor packaging found in
  this research pass.

### Capability discovery

`[Synthesis]` **No vendor researched has one unified "list everything I can
do" surface spanning skills + rules + subagents + hooks + MCP tools at
once.** Every single ecosystem has separate, per-mechanism discovery
surfaces instead (a skills panel, an MCP manager, a hooks browser, a
permissions view) — this absence is a genuine, repeatedly-confirmed
cross-ecosystem fact, not a gap in this research. Where discovery does
converge is at the skill level specifically: metadata-only indexing
up front, full content on demand, is universal (see Skills above).

### Agent-specific limitations

No single common limitation recurs verbatim, but a common **pattern**
does: every vendor's own documentation volunteers, unprompted, that its own
permission/sandbox system has known gaps or is explicitly not a security
guarantee (Cursor, Claude Code, Codex all state this in their own words);
that hooks and/or subagents are Preview/experimental/beta (VS Code hooks,
Windsurf/Devin subagents, VS Code's forked-skill-context); or that some
capability doesn't cover every surface uniformly (Codex's sandbox
excludes web/MCP/browser; VS Code's MCP sandboxing doesn't work on
Windows at all). `[Synthesis]` The honest state of the art across every
vendor researched is: **permission and sandboxing systems are young,
rapidly evolving, and self-admittedly incomplete everywhere** — this should
inform how much a vendor-neutral spec leans on any one vendor's enforcement
model as a dependable primitive.

---

## Common capabilities

Capabilities with a real, multi-ecosystem documented equivalent (not every
ecosystem needs to implement it identically — see Portability requirements
below for what "equivalent" has to mean in practice):

1. A packaged, invokable unit of instructions with `name` + `description`
   metadata and a Markdown body, discovered via cheap upfront metadata and
   loaded fully only on demand ("Skills" — converges hardest of anything
   researched, per the Headline finding).
2. A project-scoped, auto-loaded-at-session-start instructions file
   (Rules/`AGENTS.md`/CLAUDE.md-equivalent), with some notion of
   always-on vs. conditionally-activated content.
3. A user/global-scope mirror of both of the above, for one person's
   cross-project reuse.
4. MCP client support with a `mcpServers`-shaped config, stdio + remote-HTTP
   transports, and per-tool/per-server approval.
5. A permission/approval layer gating shell execution, file writes, and
   tool calls, expressed as some allow/ask/deny-style rule set — universally
   self-described by vendors as imperfect/best-effort.
6. Sub-task delegation to a narrower-context worker ("subagents"), with a
   foreground/background execution split and *some* nesting-depth cap.
7. A lifecycle-hook mechanism: external process, JSON on stdin, exit-code-2
   means block — present everywhere except the MCP protocol itself.
8. A bundling/distribution unit beyond simple folder-sharing (plugin/
   marketplace concept) for team-scale reuse.
9. Manually-invoked, saved prompt templates (slash commands) — though
   trending toward being absorbed into Skills rather than staying separate.

## Vendor-specific capabilities

Capabilities documented for one (or a small minority of) ecosystems, with
no confirmed equivalent elsewhere — these should not be assumed portable,
and several are explicitly framed by their own vendor as differentiators:

- **Claude Code**: dual memory channels (human CLAUDE.md + model-authored
  typed auto memory); fork-mode subagents that inherit the entire parent
  conversation verbatim; a five-handler-type hook system (command/http/
  mcp_tool/prompt/agent) with 30+ named lifecycle events; a five-tier
  settings precedence stack with hard-coded "stricter value always wins"
  security exceptions.
- **Cursor**: Team Rules / Team hooks / Skill marketplace as dashboard-
  managed, commercial-plan-gated distribution; a named "Instant Grep" search
  technology; prompt-type (LLM-evaluated) hooks with a `loop_limit`/
  `failClosed` config surface.
- **Codex**: TOML (not JSON) configuration; a tiered permission-profile
  system (`:read-only`/`:workspace`/`:danger-full-access`) distinct from its
  separate sandbox/network-access controls; memory intentionally
  fragmented between local and cloud/ChatGPT surfaces; subagent-delegation
  autonomy explicitly gated by model/intelligence tier rather than a user
  policy flag.
- **Windsurf/Devin**: two non-interoperating agent runtimes in one product
  mid-transition; the Agent Client Protocol (ACP) for plugging third-party
  agents into the IDE shell; enterprise remote (server-side) repo indexing
  with a "delete original code after embedding" option.
- **Antigravity**: "Knowledge Items" auto-distilled by a dedicated
  background Knowledge Subagent; "Artifacts" as a first-class, UI-rendered
  deliverable type generated during a distinct Planning Mode; Sidecars
  (persistent, cron-scheduled background processes) as a distinct
  automation primitive; a hard 10-level subagent nesting cap.
- **VS Code**: the "Agent Host" multi-harness architecture (swapping the
  underlying agent vendor — Copilot/Claude/Codex — inside one editor
  session); the Chat Participant API (`@mention` extensibility) as a
  VS-Code-extension-runtime-specific mechanism distinct from "agent
  capabilities" generally; UI-rendered `handoffs` between named custom
  agents.
- **MCP itself**: the Extensions framework (namespaced, opt-in,
  independently-versioned protocol add-ons with mandatory documented
  fallback) as a formal, spec-level pattern — no coding-agent vendor
  researched has an equivalent formalized extension mechanism for its own
  proprietary surface.

## Portability requirements

What a vendor-neutral core schema needs to hold true for a skill authored
once to actually be usable, in some form, across the ecosystems researched:

1. **Assume only metadata + Markdown body as guaranteed-portable content.**
   Everything past `name`/`description`/instructions (tool scoping,
   subagent execution, dynamic injection) is an extension in at least one
   ecosystem and must degrade gracefully where unsupported, not fail.
2. **Never assume a specific memory model, or memory at all.** This is the
   least standardized dimension researched, with one vendor actively
   removing it. A skill that depends on cross-session memory has no
   guaranteed portable target today.
3. **Never assume a semantic/embedding-based repository index exists.**
   Roughly half the ecosystems researched rely purely on agentic
   grep/read-style tools instead.
4. **Never assume a specific hook fail-open/fail-closed default.** At least
   one vendor documents defaulting fail-open; a skill relying on hooks for a
   security-relevant block must not assume the target enforces it the way
   the author's own agent does.
5. **Never assume subagents share (or don't share) parent conversation
   history.** This is a real fork in documented designs, not just naming.
6. **Never assume "commands" and "skills" are separate capabilities** — at
   least three vendors are actively merging them; author for the merged
   model, not the split one.
7. **Never assume project-level configuration/instructions apply
   unconditionally** — untrusted-project trust gating that silently drops to
   a narrower config tier is a recurring, not vendor-specific, behavior.
8. **Never assume a single discovery surface can enumerate everything a
   skill might need to know is available** — every ecosystem has
   per-mechanism discovery only.
9. **Assume tool names are never portable.** No two ecosystems share a tool
   vocabulary; any "this skill needs tool X" declaration must be expressed
   in vendor-neutral terms and resolved by an adapter, never as a literal
   tool name.

## Adapter requirements

Concrete translation work every one of the seven ecosystem docs
independently concluded an adapter would need to do — consolidated, not
re-derived:

- **Path/location mapping**: placing a skill/rule/hook/MCP-config file at
  each target's exact expected directory and filename convention (no two
  ecosystems agree, even where several ecosystems separately recognize
  `.agents/skills/` as *one of several* valid paths).
- **Frontmatter field mapping**: translating a generic "always apply" /
  "apply when relevant" / "apply to these files" / "manual only" activation
  intent into each vendor's specific field names and value grammar
  (`alwaysApply` vs. "Always On" vs. presence/absence of `globs`, etc.).
- **Tool-declaration mapping**: translating a generic "this skill needs
  these kinds of tools" statement into each target's actual tool-name
  vocabulary and permission-rule syntax (Bash wildcard grammar,
  `action(target)` strings, MCP server/tool namespacing — all mutually
  incompatible).
- **Hook-event mapping**: translating generic lifecycle points ("before a
  file write," "after task completion") into each target's specific named
  events, matcher syntax, and I/O contract — VS Code's own hook-ingestion
  layer is proof this mapping is lossy even when attempted directly by one
  of the vendors themselves.
- **Delegation-model mapping**: translating a generic "run this in
  isolation" concept onto each target's specific subagent mechanics,
  including whether conversation history is inherited and what the
  nesting/concurrency limits are.
- **Config-format mapping**: JSON almost everywhere, TOML for Codex; a
  literal serialization-format adapter step, not just a path/schema one.
- **Trust/precedence mapping**: reconciling a generic "who can configure
  this" concept with each target's specific precedence-tier count, merge-
  vs-override rules, and untrusted-project degradation behavior.
- **Distribution-unit mapping**: repackaging a generic bundle into each
  target's specific plugin/marketplace format when team-scale distribution
  is needed — no two are compatible, and some are commercial-plan-gated on
  the target side regardless of what the adapter does.

## Unresolved questions

Carried forward for follow-up before (or during) designing `core/`:

1. **Has anyone on this project read the actual agentskills.io specification
   directly?** Every claim of "adopts the open Agent Skills standard" in
   this research is sourced from a vendor's own description of adopting it,
   never from directly fetching and reading agentskills.io itself. This is
   the highest-priority gap: it's the difference between "adopt an existing
   external spec" and "design something new that happens to rhyme with six
   vendors' marketing language for a spec none of us have actually read."
2. **How different, in practice, are the six vendors' implementations of
   that standard?** Is it byte-for-byte `SKILL.md` compatibility, or loose
   convention-sharing with divergent extensions? (VS Code's own doc flags
   this exact question as unresolved even from its side.)
3. **What is the real current state of Cursor's "Memories" feature?** The
   documentation URL that used to host it now resolves to the Rules page;
   this research could not confirm removal, quiet retention, or a rename.
4. **Is Antigravity's CLI memory gap (third-party-reported) real, or an
   artifact of a specific version/surface the third party tested?** The
   official desktop-app docs and one third-party integration blog directly
   disagree.
5. **How should a vendor-neutral spec treat the MCP Legacy/Modern era
   split?** Given the 2026-07-28 revision is six weeks old and most
   deployed MCP clients/servers likely still speak the older
   handshake-based protocol, should `core/`'s MCP-facing guidance target
   Legacy, Modern, or explicitly require dual-era handling from adapters?
6. **Should "commands" exist as a distinct primitive in `core/` at all**,
   given at least three vendors are actively deprecating the standalone
   concept in favor of skills? Or should `core/` model only skills, with
   "manually-invoked-only" as one value of an activation-mode field?
7. **What should `core/` say about hooks' fail-open/fail-closed default?**
   Cursor's own docs flag this as a live security-relevant choice with no
   single right answer; a vendor-neutral spec presumably needs to require
   skill/hook authors to state their assumption explicitly rather than
   inherit whichever default the target happens to ship.
8. **Does this project want to track the Skills-over-MCP Working Group's
   SEP-2640 as it moves from "Accepted" toward a reference implementation?**
   It was accepted six days before this research and could materially
   change what "MCP support for skills" means within this project's likely
   design window.
9. **How much of this research will be stale by the time `core/` is
   designed?** Given the pace documented throughout (Cursor's Skills are
   eight months old at most by the time anyone reads this; Windsurf's
   rebrand is three months old; MCP's spec is six weeks old), a
   re-verification pass immediately before spec design — not months later —
   seems warranted rather than treating this snapshot as durable.
