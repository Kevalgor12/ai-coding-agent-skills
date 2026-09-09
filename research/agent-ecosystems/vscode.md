# VS Code / GitHub Copilot Agent Capabilities — Research Notes

Research date: 2026-09-09. Scope: VS Code's built-in/first-party AI coding-agent surface —
GitHub Copilot Chat's agent mode, VS Code's chat/extensibility APIs, and (as of the 1.10x /
"Agent Host" era) VS Code's support for running multiple agent harnesses (Copilot, Claude,
Codex) inside the editor. Third-party VS Code extensions (Cursor, Windsurf, etc.) are explicitly
out of scope, except where noted as "what they build on."

Docs move fast for this surface — the URL structure itself changed during this research
(older `code.visualstudio.com/docs/copilot/...` paths are being superseded by
`code.visualstudio.com/docs/agent-customization/...` and `code.visualstudio.com/docs/agents/...`).
Both old and new paths are cited below where both were found live.

---

## 0. Big picture: VS Code is becoming a multi-harness agent host

[Source: https://code.visualstudio.com/docs/agents/run/agent-harnesses] VS Code documents four
"agent harnesses" a user can choose between: **Local** (runs in the VS Code extension host),
**Copilot** (Copilot SDK, runs on the "Agent Host"), **Claude** (Anthropic's Claude Agent SDK,
"runs autonomously on your workspace"), and **Codex** (OpenAI Codex, via extension or
experimentally on the Agent Host). A **Cloud** target additionally allows remote execution on
provider infrastructure. Per the doc: "Your choice primarily affects where the agent runs, which
tools and models it can use, and how it applies code changes."

[Source: https://code.visualstudio.com/docs/agents/overview] VS Code frames "agents" broadly as
things that "combine language-model reasoning with tools that act on your development
environment," organized around an **Agent Loop** (reason → gather context → act → iterate),
**Sessions** (persistent containers holding conversation, workspace, changes, execution state)
that are not tied to one interface (can continue across the Chat view, a dedicated Agents
window, browser, CLI, or desktop app), and **Harnesses** that coordinate the loop.

[Source: https://code.visualstudio.com/blogs/2026/08/26/agent-host-architecture] The "Agent
Host" is described as a separate process (not the VS Code extension host) that runs harnesses
like Copilot, Claude, and Codex, built on an "Agent Host Protocol" — enabling one session to be
rendered across multiple VS Code windows simultaneously.

**Why this matters for the Skill Library project:** VS Code is not just "Copilot's editor" —
it is positioning itself as a *neutral runtime* that several different agent vendors' harnesses
plug into, each bringing their own customization surface (Claude brings `.claude/` hooks and
memory files; Codex brings its own permission presets; Copilot brings its own slash commands).
[Source: https://code.visualstudio.com/docs/agents/run/agent-harnesses] explicitly states the
docs "don't explicitly confirm whether skills, instructions, and hooks work identically across
all harnesses — they appear partially harness-specific rather than universal" (this is the
research agent's paraphrase of the fetched page, not a verbatim quote; treat as
[Inference, not confirmed in docs] regarding exact uniformity, though the partial-harness-
specificity claim itself is drawn from the doc's own comparison table).

---

## 1. Skills

[Source: https://code.visualstudio.com/docs/agent-customization/agent-skills] VS Code has an
explicit, named **"Agent Skills"** feature (experimental, introduced around VS Code 1.108,
per https://visualstudiomagazine.com/articles/2026/01/11/hand-on-with-new-github-copilot-agent-skills-in-vs-code.aspx).
This is a first-class reusable-capability concept, distinct from prompt files and custom
instructions:

- A skill is a folder containing a `SKILL.md` file with YAML frontmatter plus a Markdown body
  of instructions, optionally with additional resource files referenced via relative Markdown
  links.
- Required frontmatter: `name` (unique id, lowercase-hyphenated, ≤64 chars) and `description`
  (explains capabilities/use cases, ≤1024 chars, used for model-driven discovery).
- Optional frontmatter: `argument-hint` (placeholder text when invoked as a slash command),
  `user-invocable` (default true; set false to hide from the `/` menu while still allowing
  automatic/model-driven loading), `disable-model-invocation` (default false; set true to force
  manual-only invocation), `context: fork` (experimental — runs the skill in an isolated
  subagent, returning only the final result to the parent conversation).
- **Progressive/three-level loading model**: (1) discovery — only frontmatter `name`/
  `description` are read to match against the user's query; (2) instruction loading — the full
  `SKILL.md` body is loaded into context only when the skill is invoked or judged relevant; (3)
  resource access — any additional linked files are read only if the skill's own instructions
  reference them. This is explicitly meant to keep context usage low even with many skills
  installed.
- Storage locations — **project/workspace scope**: `.github/skills/`, `.claude/skills/`,
  `.agents/skills/` (custom paths via `chat.agentSkillsLocations` setting); **user scope**:
  `~/.copilot/skills/`, `~/.claude/skills/`, `~/.agents/skills/`. Monorepo parent-repo discovery
  can be enabled via `chat.useCustomizationsInParentRepositories`.
- Requires the `github.copilot.chat.skillTool.enabled` setting for the forked-context feature.
- **Portability claim**: [Source: https://code.visualstudio.com/docs/agent-customization/agent-skills]
  states Agent Skills follows "an open standard at agentskills.io," explicitly intended to be
  portable across GitHub Copilot in VS Code, GitHub Copilot CLI, and GitHub Copilot's cloud
  agent — i.e., VS Code did not invent a proprietary skill format but adopted (or is
  interoperating with) a cross-tool `SKILL.md` convention that overlaps directly with
  Anthropic's own Claude Skills format (same `SKILL.md` frontmatter shape, same folder-based
  packaging). This is highly relevant to a vendor-neutral skill schema — it suggests a real,
  already-converging de facto standard exists across at least two major vendors.
- Extensions can also contribute skills programmatically via a `chatSkills` contribution point
  in `package.json`, with the skill's directory name required to match the `name` field in its
  `SKILL.md`.
- Distributed via **Agent Plugins** (see §9/§ "Commands" below), plugin-provided skills get an
  automatic namespace prefix (e.g. `/my-plugin:skill-name`); manually adding a namespace prefix
  yourself causes silent load failures — noted explicitly as a footgun in the docs.
- **Relationship to prompt files**: [Source: https://code.visualstudio.com/docs/agent-customization/prompt-files]
  states "Agents running on the Agent Host don't use prompt files" — to use an existing prompt
  file with the Copilot agent on the Agent Host you must convert it to an Agent Skill instead.
  VS Code offers an experimental one-time auto-migration tool for this
  (`chat.customizations.promptMigration.enabled`). Prompt files continue to work for "local"
  agents running in the classic VS Code extension host.

**Preliminary read:** Skills are VS Code's/GitHub's answer to "reusable, discoverable agent
capability packaging," and they are explicitly designed to be more universal (via agentskills.io)
than VS Code's other customization types, several of which are VS Code/Copilot-specific.

---

## 2. Rules / project instructions / user instructions

[Source: https://code.visualstudio.com/docs/agent-customization/custom-instructions] VS Code
supports several tiers of "custom instructions":

- **Always-on / automatic instructions** (applied to every chat/agent request in a workspace,
  no invocation needed):
  - `.github/copilot-instructions.md` — single file at the workspace root, GitHub-Copilot-
    specific convention.
  - `AGENTS.md` — automatically detected at workspace root; nested variants in subfolders are
    experimental; gated by the `chat.useAgentsMdFile` setting (and `chat.useNestedAgentsMdFiles`
    for nested). Positioned explicitly for "multi-agent compatibility" — i.e. VS Code treats
    `AGENTS.md` as a cross-vendor convention, not Copilot-proprietary.
  - `CLAUDE.md` — searched in workspace root, `.claude/`, and `~/.claude/`; gated by
    `chat.useClaudeMdFile`; explicitly "compatible with Claude Code and other Claude tools" —
    VS Code directly reads a competing vendor's project-memory file format.
  - **Organization-level instructions** — defined at the GitHub organization level, gated by
    `github.copilot.chat.organizationInstructions.enabled`.
- **Conditional / path-scoped instructions**: `*.instructions.md` files in
  `.github/instructions/` (workspace) or `~/.copilot/instructions/` (user), with YAML
  frontmatter fields `name`, `description`, and `applyTo` (glob pattern(s), comma-separated;
  if `applyTo` is omitted, the file is not auto-applied — it must be attached manually or
  referenced). Application is decided either by the glob match or by "semantic matching of the
  instruction description to the current task" per
  [Source: https://code.visualstudio.com/docs/agent-customization/custom-instructions] (originally
  surfaced via `code.visualstudio.com/docs/copilot/customization/custom-instructions`, now
  redirecting to the `agent-customization` path).
  - Note: for `.claude/rules` style files a `paths` array is used instead of `applyTo` —
    i.e. VS Code normalizes across two different vendor conventions for the same concept.
- **Scope summary**: Workspace (`.github/...`, shared via version control) vs. User
  (`~/.copilot/instructions/`, not shared) vs. Organization (GitHub-org-wide). Not all
  customization types support all three scopes.
- **Precedence** (highest → lowest, as documented): personal/user-level instructions >
  repository instructions > organization instructions. Multiple instruction files are combined
  ("VS Code combines and adds them to the chat context") rather than one overriding another
  outright, except for this priority ordering when trimming for space/conflicts.
- Relevant settings: `chat.instructionsFilesLocations` (custom scan paths),
  `chat.useCustomizationsInParentRepositories` (monorepo parent discovery),
  `chat.includeApplyingInstructions`, `chat.includeReferencedInstructions`.
- Custom instructions explicitly do **not** apply to inline (ghost-text) completions — only to
  Chat/Edits/Agent requests.
- `/init` command can auto-generate a `copilot-instructions.md` by analyzing the workspace.
- [Source: https://code.visualstudio.com/docs/agent-customization/overview] confirms the Agent
  Host reads *user-level* customizations from "harness-agnostic folders like `~/.copilot`
  (Copilot) and `~/.claude` (Claude), rather than from your VS Code profile user data" when
  running on the Agent Host — i.e. user-scope storage location depends on which harness is
  active, not just on VS Code itself.

---

## 3. Context and context loading

[Source: https://code.visualstudio.com/docs/copilot/chat/copilot-chat-context (also listed as
`/docs/chat/copilot-chat-context`)] Context is assembled through several explicit mechanisms:

- **`#`-mentions**: typing `#` in the chat input opens a picker of context items — specific
  files/folders/symbols by name, or predefined dynamic items like `#changes` (diff of changed
  files), `#codebase` (semantic codebase search), and `#fetch` (retrieve a specific public URL's
  content into context, with local caching of the fetched page).
- **`@`-participants** provide domain-scoped context/orchestration rather than raw context
  injection (see §9 Commands / built-in chat participants: `@vscode`, `@terminal`, `@workspace`).
- **Agentic/automatic context gathering**: per
  [Source: https://code.visualstudio.com/docs/agents/reference/workspace-context], in agent
  mode "Copilot runs multiple tools ... reviews the results, and automatically performs
  follow-up" searches until it decides it has enough context — i.e., context assembly in agent
  mode is largely tool-call-driven rather than a single static injection step.
- Documented known UI limitation: one community/secondary source (not the primary doc) notes
  file context selection via the picker is capped at 10 files at a time — flagged here as
  weakly sourced (not from an official code.visualstudio.com page found in this research) and
  should be re-verified before relying on it.

---

## 4. Tools and tool calling

- **Built-in tools**: [Source: https://code.visualstudio.com/blogs/2025/02/24/introducing-copilot-agent-mode]
  documents agent-mode built-ins including a "Thinking Tool" (experimental extended reasoning
  between tool calls), a "Fetch Tool" (retrieve public web page content, cached locally), and a
  "Usages Tool" (combines Find All References / Find Implementation / Go to Definition).
  [Source: https://code.visualstudio.com/docs/agents/reference/workspace-context] additionally
  documents Semantic Search (`#codebase`), Text Search, Grep, File Search, "Usages," List
  Directory, and Read File as tools the agent orchestrates itself.
- **Language Model Tool API for extensions**: [Source: https://code.visualstudio.com/api/extension-guides/ai/tools]
  — extensions declare tools via the `contributes.languageModelTools` point in `package.json`,
  each with `name` (convention: `{verb}_{noun}`), `displayName`, `modelDescription` (guidance
  for the LLM on when/why to call it), `userDescription`, `icon`, and an `inputSchema` (JSON
  Schema for parameters, convention `{noun}` naming, absolute file paths recommended). Extension
  tools are one of three tool categories VS Code recognizes: (1) built-in, (2) extension-
  contributed via this API, (3) MCP server tools.
- **Confirmation/permission model for extension tools**: a generic confirmation is always shown
  unless the tool implements `prepareInvocation` for a custom confirmation message (Markdown,
  can include code blocks); the user can choose "Always Allow" to suppress future prompts for
  that tool.
- **Agent-mode-wide approval settings**: [Source: search-derived, from
  https://code.visualstudio.com/docs/agents/run/approvals and related settings docs] — a
  "Global: Auto Approve" checkbox exists (applies to all tools uniformly — VS Code's own docs
  note it currently has no per-tool granularity control), plus targeted allow/deny settings such
  as `chat.tools.urls.autoApprove` (per-URL-pattern auto-approval for the Fetch tool) and
  terminal-command allow/deny regex lists in `settings.json`. Commands exist to reset
  (`Chat: Reset Tool Confirmations`) or manage (`Chat: Manage Tool Approval`) prior approvals.
- **Tool sets / precedence**: per
  [Source: https://code.visualstudio.com/docs/agent-customization/custom-agents], when both a
  prompt file and a custom agent specify `tools`, "prompt file tools override custom agent
  tools" — giving fine-grained control (e.g. a read-only planning agent vs. a full-access
  implementation agent).
- **Chat Participant vs. Tool distinction**: [Source: https://code.visualstudio.com/api/extension-guides/ai/chat]
  explicitly distinguishes chat participants (which receive the raw user prompt and orchestrate
  their own steps) from language model tools (invoked by the LLM itself as part of its own
  orchestration loop) — these are two different extensibility mechanisms, not variations of one.

---

## 5. File access and repository understanding

[Source: https://code.visualstudio.com/docs/agents/reference/workspace-context]

- Copilot maintains a **semantic index** of the workspace; how it's built depends on the repo
  type: GitHub-hosted repos are indexed server-side by GitHub (often near-instant for smaller
  repos), Azure DevOps repos are indexed automatically with Microsoft-account sign-in, and
  local/other workspaces get a **locally built index** (initial build takes minutes, then
  updates continuously in the background).
- Multiple complementary search mechanisms are exposed to the agent: semantic search
  (`#codebase`, requires the index), plain text search, grep (exact/regex, index-independent),
  file/glob search, and a "Usages" tool (references/implementations/definitions).
- File exclusion respects `.gitignore` and the `files.exclude` setting, "though `.gitignore` is
  bypassed if you have a file open or have text selected within an ignored file."
  Binary files are automatically excluded from indexing.
- The docs claim scaling from "five files" to "500,000 files" by adapting search strategy to
  project size, but **do not specify explicit numeric limits** on repo size or context window
  usage — this is a documented gap, not a discovered limit. Not documented / could not verify:
  exact context-window ceiling for how much repository content can be included in a single
  agent turn.

---

## 6. Memory

[Source: search-derived from official-adjacent secondary sources plus corroborating VS Code
command-palette evidence (`Chat: Show Memory Files`); a canonical single `code.visualstudio.com`
memory-feature doc page was not directly fetched in this research pass, so treat the specifics
below as **moderately, not fully, confirmed** — flagged accordingly]

- VS Code has a "Memory" tool/feature (preview) with three documented scopes:
  1. **User memory** — persists across all workspaces/conversations; first ~200 lines
     auto-loaded each session.
  2. **Repository memory** — scoped to the current workspace, persists across conversations
     within that project.
  3. **Session memory** — tied to the current conversation only, cleared when the session ends.
- Accessible via Command Palette → `Chat: Show Memory Files`.
- Described as "stable for everyday use" but with an evolving feature set (e.g., individual
  file deletion not yet supported at time of writing).
- **This entire section should be treated as [Inference/weakly sourced]** relative to the rest
  of this document — it was not verified against a primary `code.visualstudio.com` page during
  this research pass; a follow-up direct fetch of the official Memory doc (if one exists at a
  stable URL) is recommended before treating these details as load-bearing.

---

## 7. Sub-agents and delegation

[Source: https://code.visualstudio.com/docs/agent-customization/custom-agents]

- **Custom agents** (formerly "chat modes" — `.chatmode.md` files should be renamed to
  `.agent.md`; functionality is identical, only naming changed) can declare an `agents`
  frontmatter field: a restricted list of subagents available for delegation, or `*` for all.
  Delegation additionally requires the built-in `agent` tool to be included in that agent's
  `tools` list.
- **Handoffs**: a documented `handoffs` frontmatter field defines guided, sequential workflow
  transitions between agents (e.g., Planning → Implementation → Code Review), each specifying a
  target agent id, a button label, an optional pre-filled prompt, optional auto-submit flag, and
  optional model override. After a response, the user sees clickable handoff buttons that
  preserve context into the next agent.
- Related setting: `chat.subagents.allowInvocationsFromSubagents` (permits nested/subagent-of-
  subagent invocation) — found in the AI settings reference
  [Source: https://code.visualstudio.com/docs/copilot/reference/copilot-settings].
- Storage: `.agent.md` files in `.github/agents` or `.claude/agents` (workspace) or
  `~/.copilot/agents` (user); custom paths via `chat.agentFilesLocations`.
- Agent Skills' `context: fork` option (§1) is a second, narrower delegation mechanism —
  running one skill invocation as an isolated subagent whose intermediate reasoning is hidden
  from the parent, returning only a final result.
- This is a real, documented multi-agent orchestration model — not merely inferred — though it
  is clearly VS-Code/Copilot-specific in its exact mechanics (frontmatter schema, button UI).

---

## 8. Hooks

[Source: https://code.visualstudio.com/docs/agent-customization/hooks] — explicitly **Preview**
status; "the configuration format and behavior might change in future releases," and
organizations can disable hooks entirely via enterprise policy.

- **Eight documented lifecycle events**: `SessionStart`, `UserPromptSubmit`, `PreToolUse`,
  `PostToolUse`, `PreCompact`, `SubagentStart`, `SubagentStop`, `Stop`.
- **Config format**: JSON, `{ "hooks": { "<EventName>": [ { "type": "command", "command": ...,
  "timeout": ..., "cwd": ..., "env": {...} } ] } }`.
- **File locations** (priority-ordered): workspace `.github/hooks/*.json` or
  `.claude/settings.json`; user `~/.copilot/hooks` or `~/.claude/settings.json`; a `hooks` field
  directly in a custom agent's `.agent.md` frontmatter; or `hooks.json`/`hooks/hooks.json` inside
  an Agent Plugin.
- **I/O contract**: hooks receive JSON on stdin (`timestamp`, `cwd`, `session_id`,
  `hook_event_name`, `transcript_path`, plus event-specific fields — e.g. `PreToolUse` includes
  a `permissionDecision` of `"allow"`/`"deny"`/`"ask"`); they may emit JSON on stdout
  (`continue`, `stopReason`, `systemMessage`) to influence agent behavior. Exit code 0 = success
  (stdout parsed as JSON), exit code 2 = blocking error (stop processing), any other code =
  non-blocking warning.
- **Explicit cross-vendor compatibility layer**: VS Code reads Claude Code's own
  `.claude/settings.json` hook config directly, but translates it — Claude Code's `snake_case`
  fields (e.g. `file_path`) become VS Code's `camelCase` (`filePath`); Claude's tool names
  (`Write`/`Edit`) map to VS Code's own tool names (`create_file`/`replace_string_in_value`-
  style); and Claude-style matchers (e.g. `"Edit|Write"`) are **parsed but not enforced** — "all
  matching hooks run regardless" per the doc, a documented behavioral gap versus Claude Code
  itself. Copilot CLI's own hook config (lowerCamelCase event names, `bash`/`powershell` command
  keys) is similarly ingested and translated (PascalCase event names; `bash`→osx/linux,
  `powershell`→windows).
- **Security guidance is explicit and strong**: hooks run with full VS Code process permissions;
  docs recommend disabling auto-approval specifically for edits to hook script files themselves,
  since an agent that can edit its own hooks could self-modify its guardrails.
- Hooks can be scaffolded via `Chat: Generate Hook` (Command Palette) or the Agent
  Customizations editor.

---

## 9. Commands (slash commands, chat participants)

- **Chat Participant API** [Source: https://code.visualstudio.com/api/extension-guides/ai/chat]:
  extensions register participants via the `chatParticipants` contribution point in
  `package.json` (`id`, `name` for the `@mention`, `fullName`, `description`, `isSticky`).
  Built-in participants: `@vscode` (VS Code/extension API questions), `@terminal` (shell/command
  expertise), `@workspace` (project/codebase understanding) — these get precedence in automatic
  participant detection, and reserved-name conflicts fall back to showing the fully-qualified
  extension id.
  - Participants contribute their own **slash commands** (e.g. `/explain`, `/teach`) with
    `name` + `description`.
  - A `ChatFollowupProvider` lets a participant suggest clickable follow-up prompts after a
    response.
- **Prompt files as slash commands** [Source: https://code.visualstudio.com/docs/agent-customization/prompt-files]:
  a `.prompt.md` file becomes invocable as `/<name>` in chat (name defaults to filename, or set
  via frontmatter `name`); also runnable via Command Palette (`Chat: Run Prompt`) or an editor
  "play" button. Frontmatter: `description`, `name`, `argument-hint`, `agent` (which agent runs
  it — `ask`/`agent`/`plan`/a custom agent name), `model`, `tools` (supports `<server>/*` for all
  tools of an MCP server). Workspace prompts live in `.github/prompts/` (+
  `chat.promptFilesLocations` for extra paths); user prompts live in the VS Code user profile.
- **Agent Skills as slash commands** (§1): unless `user-invocable: false` is set, a skill also
  appears as a `/`-invocable command; plugin-sourced skills are auto-namespaced
  (`/plugin-name:skill-name`).
- **MCP prompts** (§10) surface as `/<server>.<prompt>`.

---

## 10. MCP support

[Source: https://code.visualstudio.com/docs/agent-customization/mcp-servers (older path:
`/docs/copilot/customization/mcp-servers`); also
https://code.visualstudio.com/api/extension-guides/ai/mcp]

- **Config format**: `mcp.json` — top-level `servers` map, each entry with a `type`
  (`http`/`stdio`), plus `command`/`args` for local (stdio) servers or a URL for remote (http)
  servers.
- **Three storage tiers**: (1) **Workspace** — `.vscode/mcp.json`, intended to be checked into
  source control for team sharing; (2) **User profile** — via `MCP: Open User Configuration`,
  available across all workspaces, and VS Code notes each user *profile* can have its own MCP
  config; (3) **Remote** — an `mcp.json` on the remote machine when using VS Code Remote.
- **Input variables**: to avoid hardcoding secrets, config supports `${env:API_KEY}` (reference
  an environment variable) or `${input:ENDPOINT}` (prompt the user for a value at server start).
- **Discovery/declaration methods**: manual install from the Extensions view (`@mcp` filter),
  direct `mcp.json` editing (workspace or user), CLI `--add-mcp` flag, automatic discovery of
  servers already configured in other applications (e.g. Claude Desktop), and Dev Container
  (`devcontainer.json`) declaration.
- **Tool approval model differs by sandboxing**: unsandboxed MCP servers prompt the user to
  confirm each tool invocation (with an "Always Allow" style escape); sandboxed servers have
  their tool calls **auto-approved** because they execute in a controlled environment. Sandboxing
  is explicitly documented as **not available on Windows**, and even on macOS/Linux it only
  covers stdio-based servers.
- **MCP capabilities beyond tools** are explicitly supported: **Resources** (read-only context
  data — files, DB tables, API responses), **Prompts** (preconfigured templates surfaced as
  `/<server>.<prompt>`), and **MCP Apps** (interactive UI components rendered inline in chat).

---

## 11. Configuration (settings.json)

[Source: https://code.visualstudio.com/docs/copilot/reference/copilot-settings] The dedicated
"AI settings reference" groups settings by category:

- **General**: `chat.commandCenter.enabled`, `chat.disableAIFeatures` (kill switch for all
  built-in AI/Copilot features), `workbench.settings.showAISearchToggle`.
- **Chat**: `github.copilot.chat.localeOverride`, `chat.stickyScroll.enabled`,
  `chat.math.enabled`, `chat.artifacts.enabled` (experimental artifacts panel),
  `chat.checkpoints.enabled` (revert conversation to a prior checkpoint).
- **Agent**: `chat.agent.enabled` (VS Code 1.99+ required), `chat.agent.maxRequests` (default
  25 — a per-session tool/request budget), `github.copilot.chat.agent.autoFix`,
  `chat.subagents.allowInvocationsFromSubagents`.
- **Agent sessions**: `chat.viewSessions.enabled`, `chat.sessionSync.enabled` (sync sessions to
  GitHub across devices), `github.copilot.chat.claudeAgent.enabled` (enables the Claude harness
  inside VS Code).
- **Inline chat**: `inlineChat.defaultModel`, `inlineChat.renderMode`,
  `inlineChat.finishOnType`.
- Other settings referenced elsewhere in this doc: `chat.agentHost.enabled` (org-controlled,
  opts into the multi-harness Agent Host), `chat.tools.urls.autoApprove`,
  `chat.useAgentsMdFile`/`chat.useNestedAgentsMdFiles`/`chat.useClaudeMdFile`,
  `chat.instructionsFilesLocations`, `chat.agentFilesLocations`, `chat.agentSkillsLocations`,
  `chat.promptFilesLocations`, `chat.plugins.marketplaces`,
  `chat.useCustomizationsInParentRepositories`, `github.copilot.chat.skillTool.enabled`,
  `github.copilot.chat.organizationInstructions.enabled`,
  `chat.customizations.promptMigration.enabled`.
- **Scope**: settings.json supports the usual VS Code User vs. Workspace (`.vscode/settings.json`)
  split; several of the customization-location settings above are themselves how workspace vs.
  user *content* (instructions/prompts/skills/agents) gets discovered, layered on top of the
  ordinary settings scope mechanism.

---

## 12. Reusable instructions (prompt files, cross-project sharing)

Covered in depth in §1 and §9. Summary of the reuse story:

- **`.instructions.md`** files are the "rules" reuse primitive — scoped by glob (`applyTo`) or
  semantic matching, shareable via git (workspace) or via `~/.copilot/instructions/` (personal,
  cross-project).
- **`.prompt.md`** files are the "recipe" reuse primitive — manually invoked, parameterizable
  via `argument-hint`, shareable the same two ways, but explicitly **do not run under the Agent
  Host** (must be migrated to Agent Skills for that context) — a real, documented fragmentation
  in the reuse story depending on which harness is active.
- **Agent Skills** are positioned as the more universal/cross-tool reuse primitive going
  forward, per the agentskills.io open-standard claim (§1).
- **Agent Plugins** (§9/below) bundle multiple reusable pieces (skills + MCP servers + agents +
  hooks + slash commands) into one installable, marketplace-distributed unit —
  [Source: https://code.visualstudio.com/docs/agent-customization/agent-plugins]. Plugin
  structure: `plugin.json` (declares "Agent Plugins 1.0" schema), a `skills/` folder (portable),
  an `mcp.json` (portable), and a `com.github.copilot/` folder for VS-Code/Copilot-specific
  pieces (`agents/`, `hooks/`). Namespacing uses reverse-domain style; VS Code reads only its own
  `com.github.copilot` namespace and ignores other clients' namespaces in the same plugin package
  — explicitly designed so one plugin package stays portable across tools while still carrying
  tool-specific extras. Discovery via Extensions view `@agentPlugins` filter, the Agent
  Customizations editor, direct git-URL install, or CLI-synced installs from
  `~/.copilot/installed-plugins/`. Marketplace source configurable via
  `chat.plugins.marketplaces` (accepts `owner/repo` shorthand, HTTPS URL, SCP-style ref, or local
  path; defaults to two GitHub repos).

---

## 13. Capability discovery

- **Extension-declared capabilities** are static manifest contributions in `package.json`:
  `contributes.chatParticipants` (chat participants + their slash commands) and
  `contributes.languageModelTools` (tools, with `modelDescription` as the LLM-facing capability
  description) — [Source: https://code.visualstudio.com/api/extension-guides/ai/chat,
  https://code.visualstudio.com/api/extension-guides/ai/tools].
- **Skill-level discovery** is dynamic/semantic at runtime: only a skill's `name`+`description`
  frontmatter is loaded up front; the model uses that description text to decide relevance
  before ever loading the full skill body (§1's three-level loading model) — i.e. capability
  discovery for skills is closer to a RAG-style relevance match than a static manifest lookup.
- **MCP servers** advertise their tools/resources/prompts via the MCP protocol itself at connect
  time (standard MCP capability negotiation) — VS Code's `mcp.json` only declares *how to
  start/reach* a server, not what it can do; that's discovered live.
- **Agent Plugins** declare a top-level `plugin.json` manifest (schema "Agent Plugins 1.0") that
  enumerates the bundle's components by convention (folder names) rather than an explicit
  capability list — discovery here is directory-convention-based.

---

## 14. Agent-specific limitations (explicitly documented or strongly evidenced)

- [Source: https://code.visualstudio.com/docs/agent-customization/agent-skills] Forked skill
  context (`context: fork`) is explicitly "experimental and subject to change or removal."
- [Source: https://code.visualstudio.com/docs/agent-customization/prompt-files] Prompt files do
  not work with agents running on the Agent Host (only with "local" extension-host agents) —
  must be converted to Agent Skills.
- [Source: https://code.visualstudio.com/docs/agent-customization/hooks] Hooks are Preview;
  format/behavior may change; hook *matchers* copied from Claude Code config are parsed but not
  enforced (all matching hooks fire regardless of the matcher) — a known fidelity gap versus the
  vendor whose format is being ingested.
- [Source: https://code.visualstudio.com/docs/agent-customization/mcp-servers] MCP server
  sandboxing (which drives auto-approval) is not available on Windows at all, and even where
  available covers only stdio-based servers.
- [Source: https://code.visualstudio.com/api/extension-guides/ai/tools /
  https://code.visualstudio.com/docs/agent-customization/custom-instructions] Global auto-approve
  for tools is documented as all-or-nothing (no per-tool/per-extension granularity) as of this
  research date — an open GitHub issue (microsoft/vscode#269610) requests granular auto-approval,
  confirming this is a known, currently-unaddressed gap rather than an oversight in the docs.
- General agent-mode operational caveats (sourced from community/GitHub issue discussion rather
  than an official capabilities page, so weaker sourcing — flagged as such): agent mode will not
  start in untrusted workspaces (documented security behavior, not a bug); usage/rate limits
  apply per hour in agent mode and can hard-stop a session; long-running agent loops can get
  stuck in edit/test/revert cycles on the same failing test after a few iterations. These
  operational-limitation claims are **not from a single canonical VS Code limitations page** —
  no such consolidated "known limitations" doc page was found during this research pass. Treat
  them as [Inference from aggregated secondary/community sources, not confirmed in a single
  official doc].
- **Not documented / could not verify**: an explicit numeric context-window limit per agent
  turn; an explicit maximum number of skills/instructions files that can be loaded
  simultaneously; whether Agent Skills' "open standard" at agentskills.io has a formal versioned
  spec document (the claim of an open standard is documented, but this research did not fetch
  agentskills.io directly to verify its contents — only VS Code's own description of adopting it).

---

## Preliminary cross-ecosystem notes (to be reconciled in the comparison doc)

*(All of the below are explicitly preliminary/best-effort judgments by the research agent, not
additional documented facts — flagged per the task instructions.)*

**1. Likely universal across coding agents:**
- The basic shape of "project-scoped instructions file(s) read automatically at session start"
  (VS Code's `AGENTS.md`/`copilot-instructions.md`/`CLAUDE.md` trio all point at the same
  underlying need) seems close to universal — nearly every agent ecosystem researched elsewhere
  in this project likely has *some* equivalent.
- MCP as a tool-integration transport is explicitly cross-vendor already (VS Code, Claude
  Desktop/Code, presumably others) — this is genuinely universal today, not just "likely."
  Config file conventions (`mcp.json`, `.mcp.json`) differ by vendor but the protocol itself does
  not.
  - Basic slash-command-style invocation of a saved prompt/recipe is a recurring pattern.
  - Tool-call confirmation/approval as a concept (some notion of "ask before doing something
    risky") looks close to universal, even though the exact granularity (global toggle vs.
    per-tool vs. per-command-pattern) varies a lot.

**2. Distinctly VS-Code/vendor-specific:**
- The Agent Host / multiple-harness architecture (choosing among Local/Copilot/Claude/Codex
  harnesses inside one editor) is unusual and specific to VS Code's position as a
  vendor-neutral IDE surface — most agent CLIs/products don't have "swap the underlying agent
  vendor" as a first-class concept.
- Handoffs with clickable UI buttons between named custom agents is a VS-Code-chat-UI-specific
  mechanic.
- The exact `.prompt.md` / `.instructions.md` / `.agent.md` file-extension conventions and their
  frontmatter schemas are VS-Code/Copilot-specific surface syntax, even where the underlying
  concept (reusable prompt, conditional rule, persona) is more general.
- The Chat Participant API (`@mention` extensibility, `contributes.chatParticipants`) is a
  VS Code extension-API-specific mechanism for building UI-integrated assistants — this is a
  different axis from "agent capabilities" and more specific to VS Code-as-IDE than to
  "coding agents" generally.

**3. What should inform a vendor-neutral "core" skill schema:**
- The Agent Skills `SKILL.md` frontmatter (`name`, `description`, optional
  `disable-model-invocation`, optional forked/isolated execution context) is worth studying
  closely as a *starting point* precisely because VS Code itself frames it as adopting an
  external open standard shared with GitHub Copilot CLI and Copilot's cloud agent, and its shape
  overlaps with Anthropic's own Skills convention. A "core" schema in this project should
  probably treat `name` + `description` + a Markdown instruction body + optional linked resource
  files as the near-universal minimal skill shape, with three-level lazy loading (metadata →
  body → linked resources) as a strong, load-bearing design pattern worth adopting rather than
  reinventing.
- The distinction VS Code draws between "always-on instructions" (auto-loaded, no invocation)
  vs. "conditionally-applied instructions" (glob/semantic match) vs. "manually-invoked
  prompts/skills" (explicit `/` command) is a genuinely useful three-way taxonomy that a
  vendor-neutral spec should probably keep, since it maps to real, distinct trigger models
  rather than being an arbitrary VS Code-ism.

**4. What would require a VS-Code-specific "adapter":**
- Mapping a neutral skill/instruction file into VS Code's exact storage locations
  (`.github/skills/`, `.claude/skills/`, `.agents/skills/`, `~/.copilot/...`) and exact
  frontmatter field names (`applyTo` vs. `paths`, `agent` vs. `mode`, etc.).
  - Hooks: VS Code's own hook translation layer (event-name casing, tool-name remapping,
  matcher-non-enforcement) is itself evidence that hook semantics are *not* portable as-is
  between vendors even when VS Code tries to ingest another vendor's hook config directly — any
  neutral hook spec would need an explicit event-name and payload-shape mapping table per
  target, mirroring what VS Code had to build.
- The Chat Participant / Language Model Tool APIs are VS Code-extension-runtime-specific (they
  require a VS Code extension host, `package.json` contribution points, and the `vscode` API
  surface) — a neutral spec should not assume any of that; an adapter would need to translate a
  neutral "tool declaration" into this manifest format.
- Custom-agent `handoffs` (button-driven, UI-rendered) are a VS Code Chat UI feature, not a
  general delegation primitive — a neutral "delegate to sub-agent" concept could map to it, but
  the button/UI mechanics themselves are not portable.

**5. What should NOT be assumed to hold for other agents:**
- Do not assume other agents have VS Code's exact three-tier memory model (user/repo/session)
  or its specific 200-line auto-load behavior — this section of VS Code's own docs was only
  weakly confirmed in this research pass and, even if fully confirmed, is very VS-Code-specific
  in its numeric details.
- Do not assume other agents have an equivalent to "Agent Host" multi-harness switching — most
  ecosystems researched elsewhere in this project are single-vendor by construction (the agent
  CLI *is* the vendor), so "swap harnesses at runtime" is not a generalizable requirement.
- Do not assume other agents' hook matcher/event semantics line up with VS Code's eight lifecycle
  events — even VS Code's own docs show its hook translation of *Claude Code's* hook config is
  lossy (matchers ignored), so assuming cross-vendor hook compatibility anywhere is risky without
  explicit verification per pair of vendors.
- Do not assume the "Agent Skills open standard" (agentskills.io) is something this research
  fully verified — VS Code's own docs assert the standard and the portability claim, but this
  research pass did not independently fetch and verify agentskills.io's actual spec content, so
  the *degree* of true cross-vendor compatibility (byte-for-byte `SKILL.md` compatibility vs.
  loose convention-sharing) remains unconfirmed and should be checked directly before being
  treated as a settled cross-ecosystem fact.
