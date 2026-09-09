# Cursor — Ecosystem Research

Research pass on Cursor (the AI-powered code editor by Anysphere), based on official
documentation (docs.cursor.com / cursor.com/docs, cursor.com/help, cursor.com/changelog,
cursor.com/learn). Conducted 2026-09-09. Cursor ships fast and docs pages have moved/merged
recently (`docs.cursor.com` now largely redirects to `cursor.com/docs`), so URLs below are the
canonical `cursor.com/docs/...` form even where search results surfaced the `docs.cursor.com`
alias.

Citation format: `[Source: <url>]` precedes every documented claim. Claims without a source are
either explicitly marked `Not documented / could not verify` or `[Inference, not confirmed in
docs]`.

---

## 1. Skills

[Source: https://cursor.com/docs/skills] Cursor has a first-class "Agent Skills" feature.
A skill is described as "a portable, version-controlled package that teaches agents how to
perform domain-specific tasks," which can include scripts, templates, and reference material
the agent operates on using its own tools.

[Source: https://cursor.com/docs/skills] Skills have four defining properties: portable (work
across any agent that supports the Agent Skills standard), version-controlled (tracked in a repo
or installed from a GitHub link), actionable (can bundle executable scripts/templates), and
progressive (resources load on demand to keep context usage efficient).

[Source: https://cursor.com/docs/skills] File structure is a directory containing a required
`SKILL.md` with YAML frontmatter, plus optional `scripts/`, `references/`, and `assets/`
subdirectories.

[Source: https://cursor.com/docs/skills] Frontmatter fields: `name` (required, lowercase,
matches folder name), `description` (required), `paths` (optional glob restricting the skill to
matching files), `disable-model-invocation` (optional — forces explicit `/skill-name` invocation
only, disabling automatic model-triggered use), `icon`/`color` (optional, cosmetic — used for
Custom Mode badges).

[Source: https://cursor.com/docs/skills] Discovery locations, auto-scanned on startup:
`.agents/skills/`, `.cursor/skills/` (project-level); `~/.agents/skills/`, `~/.cursor/skills/`
(user/global level); with legacy compatibility paths `.claude/skills/` and `.codex/skills/` also
recognized. Nested skill directories are supported for monorepos, with skills scoped to their
containing directory.

[Source: https://cursor.com/docs/skills] Activation is via three paths: (1) automatic — the
agent evaluates relevance from context and description; (2) manual — typing `/skill-name` in
chat for a single message; (3) Custom Modes — using Option+Enter (Mac) / Alt+Enter (Windows) to
keep a skill active for an entire session.

[Source: https://cursor.com/docs/skills] Cursor explicitly frames Skills as an *open standard*:
"Agent Skills is an open standard for extending AI agents with specialized capabilities," and
references agentskills.io as the standard's home — i.e., Cursor is presenting this as
interoperable with other agents that adopt the same standard, not a Cursor-proprietary format.

[Source: https://cursor.com/docs/skills] There is a built-in `/migrate-to-skills` skill that
converts eligible "dynamic" rules and slash commands into the Skills format — indicating Cursor
sees Skills as the intended successor/superset of at least some rule and command use cases.

[Source: https://cursor.com/docs/skills] Team distribution: personal skills in `~/.cursor/skills/`
can sync to Cloud (background) Agents via a "Sync Skills for Cloud Agents" setting, gated by
Team/Enterprise admin controls; for team-wide distribution, skills are published to a **team
marketplace** (not simple folder sync) — Cursor keeps a team-hosted copy that members install
from.

[Source: https://cursor.com/docs/skills] Documented limitations: Cloud Agents cannot access
unsynced local skills or anything in `~/.agents/skills/`; self-hosted Cloud Agent workers need
either project-level skills or a pre-baked worker image; nested skills inherit automatic
directory-scoping (cannot be manually rescoped, per the docs excerpt retrieved).

[Source: https://cursor.com/changelog/2-4] Skills (along with Subagents and image generation)
shipped in Cursor **2.4, dated January 22, 2026** — i.e., this is a very recent addition to
Cursor, not a long-standing feature.

## 2. Rules / project instructions / user instructions

[Source: https://cursor.com/docs/context/rules] Project rules live in `.cursor/rules/` as
version-controlled `.mdc` (Markdown + frontmatter) files, and can be nested into subdirectories
(e.g. `.cursor/rules/frontend/components.mdc`). A plain `.md` file placed in `.cursor/rules` is
ignored by the rules system because it lacks the frontmatter needed to specify `description`,
`globs`, and `alwaysApply`.

[Source: https://cursor.com/docs/context/rules] Four rule application types:
1. **Always Apply** — `alwaysApply: true`; included in every chat session, ignoring
   description/glob fields.
2. **Apply Intelligently** ("agent-requested") — no glob set; the agent decides relevance from
   the rule's `description` and pulls it in when it judges the rule applicable.
3. **Apply to Specific Files** ("auto-attached") — activated automatically when a file matching
   the rule's `globs` pattern enters context.
4. **Apply Manually** — only included when a user explicitly references it via `@rule-name` in
   chat.

[Source: https://cursor.com/docs/context/rules] Frontmatter fields: `description` (string, used
for intelligent matching), `alwaysApply` (boolean), `globs` (comma-separated glob patterns, e.g.
`docs/**/*.md, docs/**/*.mdx`).

[Source: https://cursor.com/docs/context/rules] Rule scopes:
- **Project Rules** — `.cursor/rules/`, version-controlled, scoped to that codebase.
- **User Rules** — global preferences set across all projects; documented as applying only to
  Agent (Chat), *not* to Inline Edit.
- **Team Rules** — organization-wide rules created/enforced from the Cursor dashboard, available
  on Team and Enterprise plans only; admins can mark individual rules as required; Team Rules
  "take precedence to ensure organizational standards are maintained across all projects."
- **AGENTS.md** — a simpler markdown-only alternative to `.mdc` rules, placed at the project root
  or in subdirectories, supporting nested, directory-scoped instructions without needing
  frontmatter.

[Source: https://cursor.com/docs/context/rules] Precedence order when rules conflict: **Team →
Project → User**, with earlier (higher-listed) sources taking precedence.

[Source: https://cursor.com/docs/context/rules] Rules can also be created via a `/create-rule`
chat command or through the Customize sidebar's Rules panel; rules can be imported from remote
GitHub sources.

[Source: https://cursor.com/docs/context/rules] Nested-directory resolution: when nested
directories each define rules (e.g. via `.cursorrules` predecessor mechanism referenced in
search-derived material), a subdirectory rule overrides a conflicting root/ancestor rule for
files within its own scope, while non-conflicting rules merge additively. `AGENTS.md` files
placed in subdirectories apply automatically to files in that directory or its children.
[Note: this nested-resolution detail was retrieved via a WebSearch summary rather than a direct
page fetch — treat with slightly lower confidence than the frontmatter/type facts above, though
it is consistent with the rest of the rules documentation.]

[Source: https://cursor.com/docs/context/rules — via search summary] `.cursorrules` (the older,
single-file, pre-`.mdc` mechanism) is referenced as a legacy/simple alternative; the current
canonical mechanism is the `.cursor/rules/*.mdc` directory format.

## 3. Context and context loading

[Source: https://cursor.com/docs/context/@-symbols] The `@`-mention system provides five main
categories of explicit context attachment:
1. **Code references** — files/folders, e.g. `@auth.ts` or `@src/components/`, with `/` to
   navigate deeper.
2. **System context** — `@Terminals` to pull in terminal output.
3. **Conversation history** — `@Chats` to reference prior conversations.
4. **Version control** — `@Commit (Diff of Working State)` for uncommitted changes, `@Branch
   (Diff with Main)` for full branch diffs.
5. **Web content** — `@Browser` to bring in built-in browser context.

[Source: https://cursor.com/docs/context/@-symbols] Cursor's documented philosophy: `@`-mentions
are for explicitly attaching *known* relevant material; if you don't know what's relevant, "skip
it — Agent finds relevant files through its own search" rather than requiring manual tagging.
This is a notably different framing from the older "index everything, `@codebase` to search it"
model — see cross-ecosystem/versioning note below.

[Source: https://cursor.com/docs/context/@-symbols] There is a visible "context ring" UI element
showing context-window capacity usage, broken down by category: system prompt, tools, rules,
skills, and conversation history.

[Source: https://cursor.com/learn/understanding-your-codebase] Two search technologies work
together for "understanding the codebase": **Instant Grep** (a fast literal/regex search — see
Tools section) and **semantic search** ("search your codebase by meaning" when exact symbol
names are unknown). Both are described as automatic — "You don't need to configure anything or
change your behavior to use these tools. Cursor provides them automatically."

[Source: https://cursor.com/docs/agent/tools/search] Instant Grep is described as a custom
search engine that "outperforms ripgrep on large codebases," supporting full regex and
word-boundary matching, activated automatically when a symbol/function/error string is mentioned,
requiring zero configuration.

[Source: https://cursor.com/docs/agent/tools/search] Privacy: file paths are encrypted before
being sent to Cursor's servers, and code content is never stored in plaintext; a project can
supply a custom `.cursor/keys` file to control path decryption.

Not documented / could not verify (directly): whether the older embeddings-based semantic
indexing pipeline (Merkle-tree-based incremental sync, per historical Cursor docs/community
knowledge) is still the mechanism behind current "semantic search," or whether it has been
replaced/supplemented by a different architecture as of the 2026 docs. The pages fetched
describe *behavior* ("search by meaning") without re-exposing the underlying embeddings/Merkle
architecture that was documented in earlier doc versions — this may simply be because the
current page is user-facing rather than technical, not necessarily because the mechanism changed.
Flagging as an open question rather than asserting either way.

[Source: https://cursor.com/docs/agent/tools/search] For broader searches, Cursor can delegate to
an **Explore subagent** that runs in its own context window on a faster model, executes parallel
searches, and returns a summary rather than raw file contents to the main conversation — this
keeps large search operations from bloating the primary context.

[Source: https://cursor.com/docs/agent/tools/search] Multi-root workspaces are supported; each
workspace folder's context is available to Agent.

## 4. Tools and tool calling

[Source: https://cursor.com/docs/agent/tools] Documented built-in tools: search files/folders
(name search, directory listing, keyword/pattern search within files), web search (query
generation + execution), "Fetch Rules" (retrieve a specific rule by type/description), read files
(including images: .png/.jpg/.gif/.webp/.svg), edit files (suggest + auto-apply edits), run shell
commands (with configurable terminal profiles), browser control (navigate, screenshot, interact,
verify visual changes), image generation (from a text description, saved to the project's
`assets/` folder by default — introduced with the Nano Banana Pro model per changelog 2.4), and
"ask a question" (request user clarification mid-task).

[Source: https://cursor.com/docs/agent/tools] "There is no limit on the number of tool calls
Agent can make during a task."

Not documented / could not verify (in the specific page fetched): a fully itemized custom-tool
registration mechanism outside of MCP — the fetched tools page does not describe a way to define
wholly custom first-party tools; extensibility for tools appears to route through MCP (see
section 10) rather than a separate "custom tools" API.

[Source: https://cursor.com/docs/agent/security] Permission/approval model is tiered: no
approval required for reading files, searching code, or editing ordinary workspace files;
approval *is* required for anything touching sensitive data, changes to configuration files, all
terminal commands, and all MCP tool calls (first call to a server; subsequent calls governed by
Run Modes/allowlists).

[Source: https://cursor.com/docs/agent/security/run-modes — via search summary] "Run Modes"
govern how much autonomy the agent gets for shell commands, MCP tools, and fetch calls, ranging
from a simple allowlist up to "Auto-review," described as the recommended default: known-safe
calls run immediately, shell commands are sandboxed where possible (network/filesystem
restricted), and anything else routes through a classifier for a policy decision.

[Source: https://cursor.com/docs/cli/reference/permissions — via search summary /
https://cursor.com/docs/cli/reference/configuration] Permissions can be configured via a
`permissions` object (`allow`/`deny` string arrays of permission tokens, e.g. `"Shell(ls)"`) in
CLI config; at the project level *only* permissions are configurable (`.cursor/cli.json`), while
all other CLI settings must be global.

[Source: https://cursor.com/docs/agent/security] Explicit caveat: "Allowlists and autoRun
instructions are best-effort convenience and are not a security guarantee." Run Modes are
likewise called "best-effort guardrails rather than a hard security boundary."

[Source: https://cursor.com/docs/agent/security] Outbound network access from agent-run
processes is restricted by default to GitHub, direct link retrieval, and web search providers —
"Agents cannot make arbitrary network requests with default settings."

[Source: https://cursor.com/docs/agent/security] Workspace trust is disabled by default and must
be manually enabled by the user; if auto-reload is enabled, "agent changes might execute before
you can review them" (documented risk, not resolved by Cursor itself).

## 5. File access and repository understanding

See also section 3 (much of this overlaps). Key distinct points:

[Source: https://cursor.com/docs/agent/tools/search] Two complementary mechanisms: literal/regex
search via Instant Grep (a trigram-style fast index — per search-summary material, "builds a
trigram inverted index... 14x–80x faster than grep/ripgrep on indexed repos" — this specific
performance claim and "trigram inverted index" description came from a WebSearch summary of
community/docs content, not a directly fetched official page, so treat the exact mechanism
description as somewhat lower-confidence, though the existence and purpose of Instant Grep is
independently confirmed on the official tools/search page) and semantic ("by meaning") search for
when exact terms are unknown.

[Source: https://cursor.com/docs/agent/tools/search] File paths are encrypted in transit to
Cursor's servers; code content is never stored in plaintext.

Not documented / could not verify: exact current `.cursorignore` semantics, whether the historic
embeddings + Merkle-tree incremental re-sync architecture (widely described in older third-party
and historical docs) is still accurate today, or has been retired/replaced by Instant Grep for
some/all indexing purposes. Community forum threads (not official docs) do reference
"Index Repositories for Instant Grep" as a distinct, separately-toggleable indexing option from
classic codebase indexing, which suggests these may now be two parallel indexing subsystems
rather than one — but this is not confirmed on an official page fetched during this research
pass.

[Source: https://cursor.com/docs/agent/tools/search] Multi-root workspace support: each
workspace folder is separately indexed/available to Agent.

## 6. Memory

[Source: community forum content, cross-referenced against official docs attempt] Cursor
previously shipped a beta feature called **Memories** (introduced around v1.0, mid-2025):
per-project stored facts, proposed by a background model from conversation content, requiring
user approval before being saved, manageable (view/edit/delete) from Settings → Rules →
"Generate Memories" toggle.

Direct verification attempt: fetching `https://cursor.com/docs/context/memories` returned the
**Rules** documentation page instead of a Memories page — i.e., that path no longer resolves to
a dedicated Memories doc. Combined with community-forum reports ("Custom modes and memories gone
in 2.1") describing Memories being removed/altered in the Cursor 2.x line as part of a shift
toward more autonomous, self-gathering agent context, this strongly suggests **Memories is no
longer a current, independently-documented first-class feature** as of Cursor 2.x / today's docs.

This is a case where I could not find a definitive current official page confirming or denying
the feature's exact present status, so: **Not documented / could not verify** whether Memories
(a) still exists in some form but undocumented, (b) was fully removed, or (c) was folded into
another mechanism. What can be said with a citation is only that the URL that historically hosted
the Memories docs no longer serves that content [Source: https://cursor.com/docs/context/memories
(redirects/resolves to Rules content as of 2026-09-09)].

[Inference, not confirmed in docs] Cursor's current documented stance — visible in the `@`-mentions
page's framing ("Agent finds relevant files through its own search" rather than requiring manual
memory/tagging) — is consistent with a general product direction away from standing,
automatically-accumulated memory and toward rules (explicit, user-authored, version-controlled)
and per-session self-directed context gathering. This is an inference about product philosophy,
not a documented statement that Memories was deprecated for this reason.

No other persistent-memory mechanism (e.g., a distinct "Notepads" feature) appears in current
official docs found during this pass. Not documented / could not verify whether Notepads (an
older Cursor feature referenced in some third-party sources) still exists as a supported feature.

## 7. Sub-agents and delegation

[Source: https://cursor.com/docs/subagents] Subagents are specialized agents that operate in
their own isolated context window, handle a specific type of work, and return a result to the
parent agent.

[Source: https://cursor.com/docs/subagents] Three built-in automatic subagents ship with Cursor:
**Explore** (codebase search/analysis using a faster model, good for parallel searches), **Bash**
(shell command execution with isolated output), and **Browser** (browser control via MCP tools,
filters noisy DOM data before returning to the parent). These activate automatically without
configuration.

[Source: https://cursor.com/docs/subagents] Invocation: automatic delegation (the parent agent
decides based on task complexity and subagent descriptions), explicit invocation via `/name`
syntax (e.g. `/verifier confirm auth flow`) or natural-language mention, and parallel execution
via multiple simultaneous Task-tool calls in one message.

[Source: https://cursor.com/docs/subagents] Execution modes: **foreground** (blocks the parent
until the subagent finishes — for sequential work needing an immediate result) and **background**
(returns immediately, subagent keeps working independently — for long-running/parallel work).

[Source: https://cursor.com/docs/subagents] Custom subagents are configured as files at
`.cursor/agents/` (project) or `~/.cursor/agents/` (user), and Cursor also documents
cross-compatible legacy paths `.claude/agents/` and `.codex/agents/` at the project level.
Frontmatter fields: `name` (lowercase, hyphenated), `description` (drives automatic-delegation
matching), `model` (`inherit` by default, or a specific model id, optionally with bracketed
parameters like `composer-2.5[effort=high,context=300k]`), `readonly` (restricts the subagent to
no write access when true), `is_background` (enables background execution mode).

[Source: https://cursor.com/docs/subagents] Documented limitations: each subagent independently
gathers its own context, adding startup latency; running N subagents in parallel uses roughly N×
the tokens of a single agent; subagents can spawn child subagents but nesting depth is
restricted to "main agent and direct subagents only" (i.e., no deep recursive nesting); subagents
can underperform on simple tasks purely due to per-subagent context-initialization overhead.

[Source: https://cursor.com/docs/subagents] Isolation for concurrent multi-agent edits: each
subagent can be given its own Git worktree or cloud VM with a separate branch when a user
requests parallel/"swarm" work, to avoid edit conflicts.

[Source: https://cursor.com/docs/subagents] Cloud handoff: local agents can hand work to cloud
subagents via `/in-cloud` or `/autopilot` commands; these run on dedicated cloud VMs on their own
branches and use team-configured MCP servers from cursor.com/agents rather than the local
session's MCP config.

[Source: https://cursor.com/help/ai-features/background-agents] Separately from Task-tool
subagents, Cursor has "Background Agents"/"Cloud Agents": long-running agents that move a task
from the local device to the cloud, each running on its own dedicated VM with a full dev
environment, that plans, edits code, runs commands, tests its work over minutes-to-hours, and can
automatically open a pull request when done. Users can send follow-ups or "take over" an agent's
work, or stop/correct it, from a control panel (Ctrl+Shift+B / ⌘B in the editor).

[Source: https://cursor.com/docs/subagents] Best-practice guidance given by Cursor itself: write
focused subagents with single responsibilities; invest in detailed `description` fields (this is
what drives automatic delegation); keep prompts concise; version-control subagent definitions;
start with 2–3 subagents and expand only as use cases clarify; avoid vague descriptions like "use
for general tasks"; avoid creating 50+ generic subagents; avoid duplicating a slash command when
a Skill would do.

## 8. Hooks

[Source: https://cursor.com/docs/hooks] Hooks let custom scripts observe, control, or extend the
agent loop; each hook is a spawned process communicating via JSON over stdio, run before/after a
specific lifecycle point.

[Source: https://cursor.com/docs/hooks] Three hook categories:
- **Agent hooks** (fire during Cmd+K / Agent Chat): `sessionStart`, `sessionEnd`, `preToolUse`,
  `postToolUse`, `postToolUseFailure`, `subagentStart`, `subagentStop`,
  `beforeShellExecution`/`afterShellExecution`, `beforeMCPExecution`/`afterMCPExecution`,
  `beforeReadFile`/`afterFileEdit`, `beforeSubmitPrompt`, `preCompact`, `stop`,
  `afterAgentResponse`, `afterAgentThought`.
- **Tab hooks** (inline completions): `beforeTabFileRead`, `afterTabFileEdit`.
- **App lifecycle hooks**: `workspaceOpen` (fires on workspace open and on every workspace-folder
  change).

[Source: https://cursor.com/docs/hooks] Configuration file locations, in priority order highest
to lowest: (1) Enterprise/MDM system-wide config (`/Library/Application Support/Cursor/hooks.json`
on macOS, `/etc/cursor/hooks.json` on Linux/WSL, `C:\ProgramData\Cursor\hooks.json` on Windows);
(2) Team (Enterprise-only, dashboard-synced); (3) Project (`<project-root>/.cursor/hooks.json`,
checked into version control, scripts run from project root); (4) User (`~/.cursor/hooks.json`,
scripts run from `~/.cursor/`).

[Source: https://cursor.com/docs/hooks] Basic schema: a top-level `version` and a `hooks` object
keyed by hook name, each entry an array of `{command, type: "command"|"prompt", timeout,
matcher, loop_limit, failClosed}` objects.

[Source: https://cursor.com/docs/hooks] Two execution types: **command-based** (default) — a
shell script/command receiving JSON on stdin; exit code 0 = success (JSON output honored), exit
code 2 = block/deny, any other code = fail-open (allowed by default) — recommended for
security-critical hooks paired with `failClosed: true` to flip the default; and **prompt-based**
— natural-language condition evaluated by an LLM, returning `{ok: boolean, reason?}`, configured
with `type: "prompt"`, optional `model` override, `$ARGUMENTS` placeholder substituted with the
hook's input JSON.

[Source: https://cursor.com/docs/hooks] Every hook receives common fields (`conversation_id`,
`generation_id`, `model`, `model_id`, `model_params`, `hook_event_name`, `cursor_version`,
`workspace_roots`, `user_email`, `transcript_path`) plus event-specific fields; each event has a
documented input/output contract (e.g., `preToolUse` outputs `permission: "allow"|"deny"` plus
optional messages and `updated_input`; `stop` and `subagentStop` can return a `followup_message`
that auto-continues the loop, subject to a `loop_limit`, default 5).

[Source: https://cursor.com/docs/hooks] Matcher patterns let a hook entry scope itself to a tool
type (`Shell`, `Read`, `Write`, `MCP:<name>`), a subagent type (`generalPurpose`, `explore`,
`shell`), or a shell-command regex, depending on the hook.

[Source: https://cursor.com/docs/hooks] Session-scoped environment variables set by a
`sessionStart` hook propagate to later hook invocations in that session; standard env vars
exposed to hook scripts include `CURSOR_PROJECT_DIR`, `CURSOR_VERSION`, `CURSOR_USER_EMAIL`,
`CURSOR_TRANSCRIPT_PATH`, `CURSOR_CODE_REMOTE`, and an alias `CLAUDE_PROJECT_DIR` (notably reusing
Claude Code's env-var name for cross-compatibility of scripts).

[Source: https://cursor.com/docs/hooks] Cloud Agents only run **command-based** hooks, and only
from project hooks (`.cursor/hooks.json`), team hooks (Enterprise), or enterprise-managed hooks.
Explicitly **not available** in the cloud: `sessionStart`, `sessionEnd`,
`beforeMCPExecution`/`afterMCPExecution`, Tab hooks, `workspaceOpen`; prompt-based hooks are also
unsupported in the cloud (they require authentication unavailable there). Hooks do not execute
during "read-only exploratory turns" — they only start once the agent has writable environment
access.

[Source: https://cursor.com/docs/hooks] Documented third-party integrations that ship hooks:
MintMCP, Oasis Security, Runlayer, Corridor, Semgrep, Endor Labs, Snyk, 1Password.

## 9. Commands

[Source: community-derived summary, consistent with Cursor's documented file-based extensibility
pattern] Custom slash commands are stored as Markdown prompt files: project-level at
`.cursor/commands/<name>.md`, global/user-level at `~/.cursor/commands/<name>.md`. Typing `/` in
the Agent chat input scans both locations and lists them; selecting one inserts the entire file
content as the prompt, run with full project context. [Note: retrieved via WebSearch summaries
of `cursor.com/docs/cli/reference/slash-commands` and related pages rather than a direct page
fetch of that exact content — treat the exact file-naming/discovery mechanics as slightly
lower-confidence than directly-fetched claims, though multiple independent summaries agree.]

[Source: https://cursor.com/changelog/1-6] Slash commands (reusable, shareable team prompts) were
introduced in Cursor **1.6**.

[Source: https://cursor.com/docs/skills] Cursor's own migration tooling (`/migrate-to-skills`)
treats slash commands as one of two legacy mechanisms (alongside "dynamic" rules) that Skills are
meant to supersede for procedural/workflow use cases — implying Cursor now positions Skills as
the more capable mechanism, with slash commands remaining for simple, static, explicitly-invoked
prompt templates.

[Source: https://cursor.com/docs/cli/reference/slash-commands] The Cursor CLI has its own
slash-command reference distinct from the editor's, per official docs, but the fetched summary
did not include CLI-specific content beyond confirming the page's existence.

## 10. MCP support

[Source: https://cursor.com/docs/mcp] MCP (Model Context Protocol) lets Cursor connect to
external tools/data sources (e.g. Google Drive, Notion) as part of the agent's tool set.

[Source: https://cursor.com/docs/mcp] Configuration file `mcp.json`, at two possible locations:
project-level `.cursor/mcp.json` (workspace-specific) or global `~/.cursor/mcp.json`
(available everywhere). Servers can also be installed/managed via the Customize page UI.

[Source: https://cursor.com/docs/mcp] Config format keys servers under `mcpServers`; a stdio
server entry takes `command`, optional `args`, `env`, `envFile`; a remote server entry takes
`url` and optional `headers`.

[Source: https://cursor.com/docs/mcp] Three supported transports: **STDIO** (local, Cursor-managed
process, single user, launched via shell command), **SSE** (local or remote, server-deployed,
multi-user, SSE endpoint URL), and **Streamable HTTP** (local or remote, server-deployed,
multi-user, HTTP endpoint URL).

[Source: https://cursor.com/docs/mcp] MCP servers can be written in any language that can print
to stdout or serve an HTTP endpoint.

[Source: https://cursor.com/docs/mcp] Tool approval: "Cursor asks for approval before using MCP
tools by default"; users can inspect arguments before execution. Approval behavior is modulated
by Run Mode — in Auto-review mode, allowlisted tools run immediately while others go through a
classifier.

[Source: https://cursor.com/docs/mcp] OAuth for remote servers: Cursor accepts static client
credentials in config (`auth: {CLIENT_ID, CLIENT_SECRET, scopes}`); fixed OAuth redirect URLs are
`https://www.cursor.com/agents/mcp/oauth/callback` (web/Cloud Agents) and
`http://localhost:8787/callback` (desktop).

[Source: https://cursor.com/docs/mcp] Config values support interpolation:
`${env:NAME}`, `${workspaceFolder}`, `${userHome}` — for referencing secrets/paths without
hardcoding them into the checked-in config.

[Source: https://cursor.com/docs/cli/mcp] The Cursor CLI supports MCP too, and explicitly reuses
the *same* configuration as the editor — servers configured once work in both the editor and the
CLI.

[Source: https://cursor.com/docs/agent/security] All MCP tool calls require approval by default
(first call to a server, then governed by allowlist/Run Mode); an MCP allowlist can be configured
in `permissions.json`/CLI permissions to pre-approve specific tools.

## 11. Configuration

[Source: https://cursor.com/docs/cli/reference/configuration] Cursor CLI config is
"global-first, project-limited": global settings (`~/.cursor/cli-config.json` on macOS/Linux,
`%USERPROFILE%\.cursor\cli-config.json` on Windows) cover most options; project-level config
(`<project>/.cursor/cli.json`) is restricted to **permissions only** — "Only permissions can be
configured at the project level. All other CLI settings must be set globally." Env var overrides:
`CURSOR_CONFIG_DIR`, `XDG_CONFIG_HOME` (Linux/BSD).

[Source: https://cursor.com/docs/cli/reference/configuration] Format is plain JSON (no comments);
required `version` field (currently `1`); example fields include `editor.vimMode` and a
`permissions` object with `allow`/`deny` string arrays. The CLI self-repairs missing fields and
backs up corrupted config files with a `.bad` suffix before recreating them.

[Source: community-derived summary] A commonly recommended `.cursor/` project layout is:
`rules/` (project rules `.mdc` files), `mcp/` or `mcp.json` (MCP server config), `hooks.json`
(hooks config), `agents/` (subagent definitions), `skills/` (Agent Skills), `commands/` (slash
commands), and `docs/` (project documentation the agent can be pointed at). This is a synthesis
across the individual official pages above (each directory is independently documented) rather
than a single official page laying out the full tree, so the individual pieces are separately
cited above and this is the aggregate view. [Inference: this composite layout, not a verbatim
single-source quote.]

[Source: https://cursor.com/docs/context/rules] Settings precedence for rules specifically:
Enterprise (MDM, via hooks — separately documented) > Team > Project > User, for the mechanisms
that support team/enterprise tiers (rules and hooks both document this exact tier ordering
independently).

## 12. Reusable instructions (cross-project / cross-team sharing)

[Source: https://cursor.com/docs/context/rules] Team Rules: created/managed centrally via the
Cursor dashboard (Team/Enterprise plans), enforced (optionally "required") across all of an
org's projects, taking precedence over project and user rules.

[Source: https://cursor.com/docs/skills] Team skill marketplace: rather than folder-syncing,
Cursor publishes team skills to a hosted marketplace that members install from, with a
team-hosted copy maintained by Cursor — this is the documented cross-team-sharing path for
Skills specifically (distinct from Rules' direct-dashboard-push model).

[Source: https://cursor.com/docs/hooks] Team hooks: Enterprise-only, distributed via the
dashboard and synced to users, sitting between Enterprise/MDM hooks (highest priority) and
Project hooks in the precedence order.

[Source: https://cursor.com/docs/context/rules] Rules can be imported from remote GitHub
repository links (referenced on the rules page as a way to reuse rule sets across projects
without the Team-plan dashboard mechanism).

[Source: https://cursor.com/docs/skills] Skills can likewise be "installed via GitHub repository
links," i.e., a non-marketplace, non-Team-plan way to reuse a skill package across projects/teams
by pointing at a repo.

## 13. Capability discovery

[Source: https://cursor.com/docs/skills] Skills: discovered automatically at Cursor startup by
scanning the fixed set of skill directories (see section 1); no manual registration step beyond
placing files in the right location.

[Source: https://cursor.com/docs/context/rules] Rules: auto-attached/intelligently-applied rules
are discovered by Cursor scanning `.cursor/rules/`; users can also browse/manage them via the
Customize sidebar's Rules panel, and the agent has a dedicated built-in "Fetch Rules" tool
[Source: https://cursor.com/docs/agent/tools] to retrieve a rule by type/description at
inference time — i.e., discovery of *which* rule to pull in is itself a tool call the agent can
make.

[Source: community-derived summary] Slash commands: discovered by scanning `.cursor/commands/`
(project) and `~/.cursor/commands/` (user) and listed in a dropdown when the user types `/`.

[Source: https://cursor.com/docs/subagents] Subagents: discovered from `.cursor/agents/` (and
legacy `.claude/agents/`, `.codex/agents/`) plus user-level equivalents; the parent agent
performs automatic-delegation matching against each subagent's `description` field to decide
when to invoke one without an explicit `/name` call.

[Source: https://cursor.com/docs/mcp] MCP tools: surfaced to the agent as "Available Tools" once
a server is configured/connected; Cursor documents that the agent "automatically uses MCP tools
listed under Available Tools when relevant, including in Plan Mode," and a user can also ask for
a specific tool by name.

There is no single unified "capability index" page/API documented that lists rules + skills +
commands + subagents + MCP tools together for an external caller — each mechanism has its own
discovery path, surfaced to the *end user* mainly through the Customize sidebar and the `/`
command palette, and to the *model* through per-mechanism automatic-matching logic (rule
`description`, skill `description`, subagent `description`) plus the "Fetch Rules" tool. Not
documented / could not verify: any explicit, queryable "list all available skills/rules/tools"
API intended for programmatic (non-UI, non-model) introspection.

## 14. Agent-specific limitations

[Source: https://cursor.com/docs/agent/security] Run Modes / allowlists are explicitly described
as "best-effort guardrails," not a hard security boundary; outbound network access is restricted
by default to GitHub, direct link retrieval, and web search providers, and workspace trust is off
by default and must be manually enabled.

[Source: https://cursor.com/docs/subagents] Subagent nesting depth is restricted to "main agent
and direct subagents only" — no deep recursive sub-subagent chains; parallel subagents scale
token cost roughly linearly (N subagents ≈ N× tokens); each subagent pays a context-gathering
startup cost, which the docs say can make subagents net-slower than a single agent for simple
tasks.

[Source: https://cursor.com/docs/hooks] Several hook events are cloud-agent-unsupported entirely
(`sessionStart`, `sessionEnd`, MCP hooks, Tab hooks, `workspaceOpen`, and all prompt-based hooks);
hooks generally don't run during read-only/exploratory turns, only once the agent has write
access to the environment.

[Source: https://cursor.com/docs/skills] Cloud Agents cannot see unsynced local skills or
anything under `~/.agents/skills/`; self-hosted Cloud Agent workers need project-level skills or
a pre-baked image — global/user-level skills don't reach them by default.

[Source: search-summary of Cursor SDK docs] For the separate Cursor **Agent SDK** product (not
the editor itself): team-admin API keys are not yet supported for SDK auth; tool-call schemas are
explicitly documented as unstable and should be parsed defensively; the SDK is officially
TypeScript-only (no official Python/other-language SDK); no integration with external secret
managers (Vault, AWS Secrets Manager), no secret rotation, no VPC peering/private endpoints/
service mesh — reaching an internal API behind a corporate firewall requires a workaround (e.g.
Tailscale) rather than a supported feature; each agent VM is a single isolated environment with
no deployment pipeline or managed multi-service environment; documentation for non-trivial
patterns (long-running agents, multi-agent orchestration, custom tool registration) is described
by third parties as sparse. [Retrieved via WebSearch summary rather than a direct fetch of the
SDK docs page — flagging as slightly lower confidence, and noting this is about the *separate*
SDK product, not the editor/CLI agent described elsewhere in this document.]

[Source: https://cursor.com/docs/context/rules] User Rules apply only to Agent/Chat, not to
Inline Edit — an explicitly documented scope gap within Cursor's own feature set.

---

## Preliminary cross-ecosystem notes (to be reconciled in the comparison doc)

*(All points below are best-effort and preliminary — flagged per the instructions as informal
groundwork for a later, more careful comparison document, not a final analysis.)*

**1. Capabilities that look likely universal across coding agents:**
- Some form of project-scoped, file-based "instructions" mechanism (Cursor's Rules /
  `AGENTS.md`) — nearly every agent ecosystem researched elsewhere in this project seems to have
  an equivalent (system prompt injection from checked-in files).
- MCP client support — MCP is an open protocol, and Cursor's implementation (mcp.json,
  stdio/SSE/HTTP transports, per-tool approval) looks close to a "reference" MCP client
  implementation likely shared in spirit (if not exact config format) by other agents.
- A tool-approval / permission gate on shell commands and destructive actions — some flavor of
  "ask before running commands" seems near-universal.
- Slash commands as saved, reusable prompt shortcuts.
- Sub-agent delegation for isolating context/work (explore/search subagent, background/cloud
  agent) — the general pattern of "spin off isolated workers with their own context" recurs
  across ecosystems, even if naming and mechanics differ.

**2. Capabilities that look distinctly Cursor-specific / vendor-specific:**
- The specific `.mdc` frontmatter dialect and its four named rule-application modes (Always /
  Apply Intelligently / Apply to Specific Files / Apply Manually) — the *behavior* (auto vs.
  manual vs. glob-scoped inclusion) may generalize, but the exact frontmatter schema and file
  extension are Cursor's own.
- Team Rules / Team hooks / Skill marketplace as dashboard-managed, Team/Enterprise-plan-gated
  distribution mechanisms — this is tied to Cursor's specific commercial plan structure.
- The Enterprise MDM-managed hooks.json path (OS-specific system directories) — a Cursor-specific
  enterprise deployment detail.
- Instant Grep as a named, specific search technology with a stated (if unverified in depth)
  trigram-index implementation.
- The precise hook event taxonomy and JSON stdin/stdout contract, `$ARGUMENTS` substitution for
  prompt-type hooks, and the `loop_limit`/`failClosed` config knobs — plausible that other agents
  have *some* hook system, but this exact shape is Cursor's.
- Cloud/Background Agents as dedicated per-task VMs with git-branch-per-agent and automatic PR
  creation is a specific product shape, not obviously the same as every other vendor's
  "background agent" offering.

**3. What seems like it should inform a vendor-neutral "core" skill schema:**
- The Skills feature is explicitly framed by Cursor itself as an "open standard" (referencing
  agentskills.io), with a `SKILL.md` + frontmatter (`name`, `description`, plus optional
  `paths`/`disable-model-invocation`) + `scripts/`/`references/`/`assets/` layout, and
  progressive/on-demand loading of those subdirectories. Given Cursor explicitly says this
  standard is meant to be shared across agents, this format (or something very close to it) is a
  strong, directly-relevant candidate baseline for this project's own vendor-neutral schema — it
  may be worth checking directly whether "Agent Skills"/agentskills.io *is* effectively what this
  Skill Library project should adopt or align with, rather than reinventing an equivalent format.
- The distinction Cursor draws between three activation modes (auto/model-decided vs.
  explicit-manual vs. mode-persistent) for skills, and separately between four
  always/intelligent/glob/manual modes for rules, both point to a generalizable idea: a
  reusable-instruction schema probably needs an explicit "activation mode" field, independent of
  content, and probably needs *two* content tiers — "always-relevant persistent instructions" vs.
  "on-demand, progressively-loaded procedural packages" — since Cursor itself seems to be
  converging Rules and Skills toward exactly that division (see the `/migrate-to-skills` tool).
- A `description` field used purely to drive automatic relevance-matching (used identically for
  Rules, Skills, and Subagents in Cursor) looks like a strong universal primitive: separate the
  "what this does, for matching purposes" text from the "instructions/content" body.

**4. What would require a Cursor-specific "adapter" to translate a generic skill into something Cursor can consume:**
- Mapping a generic "always apply this instruction" concept into Cursor's specific `alwaysApply:
  true` frontmatter key, vs. mapping a generic "load only when relevant" concept into Cursor's
  no-glob + `description`-driven "Apply Intelligently" mode, vs. mapping "load only for these file
  types" into `globs`.
- Placing files into Cursor's specific expected directories (`.cursor/skills/`, `.cursor/rules/`,
  `.cursor/agents/`, `.cursor/commands/`, `.cursor/hooks.json`, `.cursor/mcp.json`) — a generic
  skill package would need an adapter step that knows Cursor's exact directory conventions and
  legacy-compatible aliases (`.claude/...`, `.codex/...`) it also happens to honor.
- Translating a generic "this skill can run scripts" capability into Cursor's specific tool-
  approval/Run-Mode/permissions.json gating model, since Cursor requires explicit
  approval/allowlisting for shell and MCP tool calls by default.
- Translating a generic hook/lifecycle-event concept into Cursor's specific event names
  (`preToolUse`, `subagentStart`, etc.) and its specific JSON stdin/stdout contract and exit-code
  semantics (0/2/other).
- Translating a generic "custom tool" concept into an MCP server registration in `mcp.json`,
  since Cursor does not appear to expose a first-party "define an arbitrary custom tool" API
  outside of MCP.

**5. What about Cursor's behavior should NOT be assumed to hold for other agents:**
- The specific tiered plan-gating (Team Rules, Team hooks, Skill marketplace all requiring
  Team/Enterprise plans) is a Cursor commercial-product detail, not a property of "rules" or
  "skills" as abstract concepts.
- The claim that Memories was introduced and then apparently removed/de-emphasized in Cursor
  2.x should not be read as evidence that *other* agents don't have or won't keep a persistent-
  memory feature — this looks like a Cursor-specific product pivot (toward self-directed context
  gathering), not an industry-wide trend confirmed by this research pass alone.
- The exact hook fail-open/fail-closed default behavior (unrecognized exit codes fail *open* by
  default) is a specific, security-relevant Cursor design choice — other agents' hook/permission
  systems may default the opposite way (fail-closed), and this should be checked per-ecosystem
  rather than assumed.
- The "best-effort, not a security guarantee" framing Cursor applies to its own allowlists/Run
  Modes is Cursor's own explicit caveat about *its own* system — it shouldn't be assumed other
  agents either share this weakness or lack it; each ecosystem's permission model needs its own
  verification.
- The specific subagent-nesting-depth restriction (only one level deep) and the "~5x token cost
  for 5 parallel subagents" scaling behavior are implementation details of Cursor's current
  subagent runtime, not necessarily true of other agents' delegation models (some may support
  deeper nesting, or have different cost/latency tradeoffs).
