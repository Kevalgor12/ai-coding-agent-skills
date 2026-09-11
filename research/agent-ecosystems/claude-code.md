# Claude Code — Ecosystem Research

Research date: 2026-09-09. Primary sources: `code.claude.com/docs/en/*` (the current canonical Claude Code docs host), `platform.claude.com/docs/en/*` (Agent Skills / API-level docs), `docs.claude.com` (redirects/mirrors some of the same content), `github.com/anthropics/claude-code`. All claims below are tagged per the citation convention requested: `[Source: <url>]` for documented facts, `[Inference, not confirmed in docs]` for reasoning, and "Not documented / could not verify" where search did not turn up an authoritative answer.

Note on doc host: Anthropic appears to have migrated primary Claude Code docs from `docs.claude.com/en/docs/claude-code/...` to `code.claude.com/docs/en/...`. Both were checked; `code.claude.com` had the more current/detailed content and is cited throughout.

---

## 1. Skills (SKILL.md mechanism)

[Source: https://code.claude.com/docs/en/skills] A Skill is a directory containing a `SKILL.md` file (YAML frontmatter + Markdown instructions), optionally with supporting files (`reference.md`, `scripts/`, etc.). Frontmatter fields are all optional but `description` is recommended since it drives automatic invocation matching.

**Storage / discovery locations**, in precedence order (Enterprise > Personal > Project > Bundled):
- Personal: `~/.claude/skills/<name>/SKILL.md` — all projects on the machine
- Project: `.claude/skills/<name>/SKILL.md` — this repo, loaded from the launch directory up to the repo root
- Enterprise: `.claude/skills/<name>/` under the managed settings directory — all users org-wide
- Nested: `<subdir>/.claude/skills/<name>/SKILL.md` — loads lazily when Claude reads files in that subdirectory
- Additional directory: via `--add-dir` — that session only
- Plugin: `<plugin>/skills/<name>/SKILL.md` — invoked as `/plugin-name:skill-name`
- claude.ai account (synced skills) — for Cowork/cloud sessions, or locally only with `CLAUDE_CODE_SYNC_SKILLS=1`

[Source: https://code.claude.com/docs/en/skills] Notable frontmatter fields beyond `name`/`description`: `disable-model-invocation` (only user can invoke via `/name`), `user-invocable: false` (only Claude can invoke), `allowed-tools`/`disallowed-tools` (scoped tool grants that clear after the next message), `context: fork` + `agent:` + `background:` (run the skill in an isolated subagent), `model`, `effort`, `paths` (glob-based auto-activation), `hooks` (register hooks for the skill's lifetime), `arguments` (named positional args), `metadata`, `license`, `compatibility`.

[Source: https://code.claude.com/docs/en/skills] Invocation is either automatic (Claude matches the user's request against loaded skill `description`s) or manual (`/skill-name [args]`). Skills can be stacked in one message (up to 6, as of v2.1.199+). Dynamic context injection is supported via `` !`shell command` `` lines that execute before Claude sees the skill content; this can be disabled with `disableSkillShellExecution: true`.

[Source: https://code.claude.com/docs/en/skills] Persistence/context behavior: once invoked, rendered `SKILL.md` content enters the conversation as a message and is **not** re-read on later turns. Skill descriptions (the index used for auto-invocation) do **not** survive `/compact`; only skills already invoked get re-injected (capped at 5,000 tokens each, 25,000 total).

[Source: https://code.claude.com/docs/en/skills] Anthropic states: "Claude Code skills follow the Agent Skills open standard, which works across multiple AI tools," extending it with invocation control, subagent execution, and dynamic context injection. See the separate open spec at agentskills.io (not verified directly in this research pass). For claude.ai upload / Skills API distribution, only a reduced frontmatter subset is honored (`name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`).

[Source: https://code.claude.com/docs/en/skills] Bundled skills ship with the product: `/run`, `/verify`, `/run-skill-generator`, `/debug`, `/code-review`, `/batch`, `/doctor`, `/workflow-authoring`. `disableBundledSkills` turns these off except `/doctor`. Live file-watching auto-reloads skill directories mid-session (with some exceptions for plugin-bundled hooks/MCP/agents, which need `/reload-plugins`).

---

## 2. Rules / project instructions / user instructions (CLAUDE.md, settings hierarchy)

[Source: https://code.claude.com/docs/en/memory] `CLAUDE.md` is the project/user/org instruction file, loaded at the start of every session (as a **user message after the system prompt**, not part of the system prompt itself — this affects how strictly it's followed).

**CLAUDE.md scopes**, loaded broadest-to-narrowest (later = read last = highest apparent salience, though all are concatenated, not overridden):
1. Managed policy: `/Library/Application Support/ClaudeCode/CLAUDE.md` (macOS), `/etc/claude-code/CLAUDE.md` (Linux/WSL), `C:\Program Files\ClaudeCode\CLAUDE.md` (Windows) — org-wide, cannot be excluded by users
2. User: `~/.claude/CLAUDE.md` — personal, all projects
3. Project: `./CLAUDE.md` or `./.claude/CLAUDE.md` — team-shared via VCS
4. Local: `./CLAUDE.local.md` — personal, project-specific, gitignored

[Source: https://code.claude.com/docs/en/memory] All discovered `CLAUDE.md`/`CLAUDE.local.md` files in the directory hierarchy from filesystem root down to the working directory are **concatenated**, not overridden — ancestor files appear first, the working directory's file last, and `CLAUDE.local.md` after `CLAUDE.md` at each level. Nested `CLAUDE.md` files (in subdirectories under cwd) load lazily when Claude reads files there. `@path/to/file` import syntax pulls in additional files (max recursion depth 4); imports from outside the working directory trigger a one-time approval dialog (except in Cowork sessions, where external imports are skipped entirely).

[Source: https://code.claude.com/docs/en/memory] `AGENTS.md` is **not** read natively by Claude Code — teams reading `AGENTS.md` must import it via `@AGENTS.md` in `CLAUDE.md` (or symlink). `/init` can read Cursor rules, Copilot instructions, and (with `CLAUDE_CODE_NEW_INIT=1`) `AGENTS.md`, `.devin/rules/`, `.windsurf/rules/`/`.windsurfrules`, `.clinerules`, folding relevant parts into a generated `CLAUDE.md`. `/import` (v2.1.213+) can additionally carry over MCP servers, commands, subagents, and skills from another agent's config.

[Source: https://code.claude.com/docs/en/memory] `.claude/rules/*.md` lets teams split instructions into topic files, optionally scoped to file globs via `paths:` frontmatter (loads only when Claude touches matching files — this is the main way Claude Code keeps large instruction sets out of context by default). User-level `~/.claude/rules/` exists too. Recommended size: CLAUDE.md under 200 lines; hard skip above 4 MiB.

[Source: https://code.claude.com/docs/en/settings, https://code.claude.com/docs/en/settings-reference] Separate from CLAUDE.md, general **settings** (`settings.json`) have their own five-level precedence stack, highest first:
1. Managed settings (`managed-settings.json`, MDM, or server-managed via claude.ai console) — org, cannot be overridden except for a short list of security-sensitive keys where the *stricter* value from a lower scope wins (e.g. `disableClaudeAiConnectors`, `isolatePeerMachines`)
2. Command line (`claude --settings '{...}'`) — one session
3. Project local (`.claude/settings.local.json`) — personal, this project, normally gitignored automatically
4. Shared project (`.claude/settings.json`) — team, committed
5. User (`~/.claude/settings.json`) — personal, every project

List-valued keys (e.g. `permissions.allow`) **merge** across scopes rather than overriding; a few keys (e.g. `fallbackModel`, `modelPicker`, `availableModels`) are exceptions that take the whole value from one scope. A fifth file, `~/.claude.json`, holds session/MCP/trust state and is managed by the CLI itself, not hand-edited.

---

## 3. Context and context loading

[Source: https://code.claude.com/docs/en/context-window] At session start, before any user prompt, Claude Code loads (in order): system prompt → auto memory (`MEMORY.md`, first 200 lines/25KB) → environment info (cwd, platform, shell, OS, git status) → MCP tool names (schemas deferred/loaded on demand unless `ENABLE_TOOL_SEARCH` overridden) → skill descriptions (one-liners, not full content) → `~/.claude/CLAUDE.md` → project `CLAUDE.md`. Nested/path-scoped CLAUDE.md and `.claude/rules/` load on demand as Claude reads matching files.

[Source: https://code.claude.com/docs/en/memory] `/context` shows what actually loaded for the current session; `/compact` replaces the conversation with a structured summary. What survives `/compact`: the startup auto-loads (system prompt, memory, CLAUDE.md — project-root CLAUDE.md is **re-read from disk** post-compact), a small number of most-recently-modified files (re-read), rules matching those files, and the body of any skill actually invoked (capped 5,000 tokens/skill). What does **not** survive: full tool-call history/outputs, the skill *description* index (only invoked skills are restored), nested CLAUDE.md/path rules that haven't re-matched a file yet.

[Source: https://code.claude.com/docs/en/hooks] `PreCompact`/`PostCompact` hooks fire around compaction, and `InstructionsLoaded` fires whenever an instruction file is (re)loaded, letting teams audit exactly what's in context.

[Source: https://code.claude.com/docs/en/memory] Separate from CLAUDE.md, **auto memory** is a second, Claude-authored memory mechanism (see Section 5).

---

## 4. Tools and tool calling

[Source: https://code.claude.com/docs/en/tools-reference] Built-in tools include, by category:
- File: `Read` (text/images/PDF/notebooks, partial reads), `Write`, `Edit` (exact-string replace, requires a prior `Read`), `NotebookEdit`
- Search: `Grep` (ripgrep syntax), `Glob` (capped at 100 results)
- Shell: `Bash` (2-min default timeout, 5GB output cap, no persisted env vars between calls), `PowerShell`, `Monitor` (background process/log watcher)
- Web: `WebFetch` (HTML→Markdown via a smaller model, lossy by design, private-address denial), `WebSearch`
- Planning/tasks: `TaskCreate/Get/List/Update/Stop`, deprecated `TodoWrite`
- Agents/collab: `Agent` (spawn subagent), `SendMessage`, `ListAgents`
- Output/content: `Artifact`, `SendUserFile`, `PushNotification`
- Code intelligence: `LSP` (jump-to-def, references, etc., requires a language plugin)
- Workflow/plan: `EnterPlanMode`, `ExitPlanMode`, `EnterWorktree`, `ExitWorktree`, `Workflow`, `CronCreate/Delete/List`, `ScheduleWakeup`
- Misc: `SendFeedback`, `ReportFindings`, `Skill`, `AskUserQuestion`, `EndConversation`, `RemoteTrigger`, `ShareOnboardingGuide`, `ListMcpResourcesTool`, `ReadMcpResourceTool`, `ToolSearch`, `WaitForMcpServers`

[Source: https://code.claude.com/docs/en/permissions] Custom/MCP tools are exposed the same way as built-ins for permission purposes: `mcp__<server>__<tool>` naming. Tools follow a tiered permission model — read-only tools (Read, Grep) generally don't prompt within the working directory; Bash/Edit/Write/WebFetch/WebSearch prompt by default in Manual mode except for a curated allowlist of read-only Bash commands and pre-approved doc domains for WebFetch.

[Source: https://code.claude.com/docs/en/permissions] **Permission model**: rules are `Tool` or `Tool(specifier)`, evaluated deny → ask → allow (first match wins, deny always wins regardless of specificity). Modes: `default`/`manual` (prompt per tool), `acceptEdits`, `plan` (read-only), `auto` (classifier auto-approves), `dontAsk` (auto-deny unless pre-approved), `bypassPermissions` (skip almost everything — explicitly documented as unsafe outside sandboxes). Permission enforcement happens in the Claude Code **client**, not the model — "Instructions in your prompt or CLAUDE.md shape what Claude tries to do, but they don't change what Claude Code allows."

[Source: https://code.claude.com/docs/en/permissions] Fine-grained rule syntax exists per tool type: Bash/PowerShell wildcard command matching (with documented parsing of compound commands, wrapper-stripping like `timeout`/`time`/`nice`, redirect-target checks), Read/Edit gitignore-style path patterns with `//`, `~/`, `/`, and relative anchors, WebFetch `domain:` patterns, MCP server/tool patterns, and `Agent(AgentName)` rules to gate subagents.

---

## 5. File access and repository understanding

[Source: https://code.claude.com/docs/en/permissions] File access is scoped to "working directories": the launch directory by default, extendable via `--add-dir`, `/add-dir`, or `permissions.additionalDirectories`. Read-only tools don't prompt inside working directories; edits do (subject to permission mode). `permissions.blockReadsOutsideWorkingDirectories` can hard-fence reads.

[Source: https://code.claude.com/docs/en/tools-reference] There is no separate embedding-based semantic index described in the docs found — repository understanding is achieved via the agentic loop itself: `Grep`/`Glob` for search (ripgrep-backed, respects `.gitignore` for Grep by default), `Read` for file content, and `LSP` tool for symbol-level navigation (jump-to-definition, find references, call hierarchy) when a language-specific code-intelligence plugin is active. **Not documented / could not verify**: any standing vector-embedding index of the repo (no evidence found of a persistent semantic/embedding index comparable to some competing tools — Claude Code's approach appears to be agentic file traversal + LSP rather than pre-built RAG over the codebase).

[Source: https://code.claude.com/docs/en/permissions] Edits go through the `Edit`/`Write`/`NotebookEdit` tools, gated by the permission system; Bash is also tracked for file-touching redirects (`> file`, `< file`), which are checked against the same Edit/Read rules.

---

## 6. Memory (persistent memory beyond CLAUDE.md)

[Source: https://code.claude.com/docs/en/memory] "Auto memory" is a second, Claude-authored persistent memory system, complementary to (human-authored) CLAUDE.md. Claude autonomously records four kinds of notes, tagged via a `type` frontmatter field: `user` (role/expertise/preferences), `feedback` (corrections/confirmed approaches), `project` (ongoing work/deadlines/decisions not derivable from code), `reference` (external pointers like issue trackers). It explicitly skips anything derivable from the codebase or already in CLAUDE.md.

[Source: https://code.claude.com/docs/en/memory] Storage: `~/.claude/projects/<project>/memory/`, keyed off the git repo (shared across worktrees/subdirectories of the same repo), containing an index `MEMORY.md` (auto-loaded, first 200 lines/25KB) plus per-topic files (loaded on demand via normal file tools, not at startup). Configurable via `autoMemoryEnabled` (on by default), `autoMemoryDirectory`. Excluded from the session-transcript retention cleanup sweep, so memory persists indefinitely until edited/deleted. `/memory` command browses/edits it; `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` disables via env var.

[Source: https://code.claude.com/docs/en/sub-agents] Subagents can have their own **separate** persistent memory, enabled per-subagent via a `memory: user|project|local` frontmatter field, stored at `~/.claude/agent-memory/<agent-name>/` (user), `.claude/agent-memory/<agent-name>/` (project, shareable via git), or `.claude/agent-memory-local/<agent-name>/` (local). The main conversation's auto memory is explicitly **not** loaded into non-fork subagents.

[Source: https://code.claude.com/docs/en/memory] Both CLAUDE.md and auto memory are explicitly documented as **context, not enforced configuration** — "To block an action regardless of what Claude decides, use a PreToolUse hook instead."

---

## 7. Sub-agents and delegation

[Source: https://code.claude.com/docs/en/sub-agents] Subagents are Markdown files with YAML frontmatter (`name`, `description`, `tools`/`disallowedTools`, `model`, `permissionMode`, `maxTurns`, `skills`, `mcpServers`, `hooks`, `memory`, `background`, `effort`, `isolation`, `color`, `initialPrompt`), invoked via the `Agent` tool. Built-in subagents: `Explore` (read-only, fast search), `Plan` (read-only, plan-mode research), `general-purpose` (full tool access, configurable model via `CLAUDE_CODE_SUBAGENT_MODEL`). Explore/Plan skip CLAUDE.md and git-status loading for speed/cost.

[Source: https://code.claude.com/docs/en/sub-agents] Definition scopes, highest priority first: managed settings > `--agents` CLI JSON (session-only) > `.claude/agents/` (project) > `~/.claude/agents/` (user) > plugin `agents/`.

[Source: https://code.claude.com/docs/en/sub-agents] Context isolation: a normal (non-fork) subagent gets its own system prompt (not the main session's), the delegation task message, the full CLAUDE.md hierarchy (except Explore/Plan), a git-status snapshot from parent-session start, and any preloaded skills — but **not** the main conversation's history, output style, auto memory, or full context window. A **fork** (`context: fork` in a skill, or the `fork` agent type) instead inherits the entire parent conversation (system prompt, tools, model, message history); only its final result re-enters the main conversation.

[Source: https://code.claude.com/docs/en/sub-agents] Execution modes: foreground (blocks main conversation) vs. background (runs concurrently; restricted to a smaller tool set: `Read, Grep, Glob, Bash, PowerShell, Edit, Write, NotebookEdit, WebFetch, WebSearch, TodoWrite, Skill, ToolSearch, EnterWorktree, ExitWorktree, Monitor, TaskStop, SendMessage`, plus MCP tools). Default: fork mode ON in interactive sessions → subagents default to background; non-interactive (`-p`) sessions default subagents to foreground.

[Source: https://code.claude.com/docs/en/sub-agents] Nesting limit: 3 layers deep by default (`CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH`); concurrency limit: 20 simultaneous subagents by default (`CLAUDE_CODE_MAX_CONCURRENT_SUBAGENTS`), exempt for `ultracode` effort sessions. At the depth limit the `Agent` tool itself is withheld (except forks). Subagents (except built-in Explore/Plan) can be resumed via `SendMessage` to their agent ID/name; transcripts persist at `~/.claude/projects/{project}/{sessionId}/subagents/agent-{agentId}.jsonl` for a 30-day default retention.

[Source: https://code.claude.com/docs/en/permissions] Subagents can be individually denied via `Agent(AgentName)` deny rules, or entirely via a deny rule on the bare `Agent` tool.

---

## 8. Hooks (lifecycle hooks)

[Source: https://code.claude.com/docs/en/hooks] Hooks are user-defined handlers — `command` (shell), `http` (POST to an endpoint), `mcp_tool` (call an MCP tool), `prompt` (ask the model), or `agent` (spawn a subagent, experimental) — that fire at specific lifecycle events, configured under a `hooks` key with `matcher` groups.

[Source: https://code.claude.com/docs/en/hooks] Event families:
- Per session: `SessionStart`, `SessionEnd`, `Setup`
- Per turn: `UserPromptSubmit`, `Stop`, `StopFailure`
- Per tool call: `PreToolUse` (blockable), `PostToolUse`, `PostToolUseFailure`, `PermissionRequest`, `PermissionDenied`, `PostToolBatch`
- Other: `UserPromptExpansion`, `SubagentStart/Stop`, `TaskCreated/TaskCompleted`, `PreModelSwitch/PostModelSwitch`, `FileChanged`, `ConfigChange`, `CwdChanged`, `Notification`, `MessageDisplay`, `Elicitation/ElicitationResult`, `PreCompact/PostCompact`, `WorktreeCreate/WorktreeRemove`, `InstructionsLoaded`, `DirectoryAdded`, `TeammateIdle`

[Source: https://code.claude.com/docs/en/hooks] Hooks receive JSON on stdin (session/tool metadata) and can return JSON with `hookSpecificOutput.permissionDecision` (`allow|deny|skip`), `additionalContext` (injected into Claude's context), `updatedInput`, etc. Exit code 2 blocks the action on supported events (e.g., `PreToolUse`); on `PostToolUse` it can only surface stderr since the tool already ran. Hooks can be scoped globally (settings files, all levels), via plugins, or per-skill/per-subagent frontmatter (skill hooks persist for the session unless `once: true`; subagent hooks apply only while that subagent is active).

[Source: https://code.claude.com/docs/en/permissions] Hooks interact with, but do not override, the permission-rule engine: a `PreToolUse` hook can add a deny/prompt, but a matching deny/ask permission **rule** still applies even if the hook says "allow." Managed/admin-enforced hooks cannot be disabled by end users; `disableAllHooks` turns off all non-managed hooks.

---

## 9. Commands (slash commands)

[Source: https://code.claude.com/docs/en/slash-commands] Two kinds: fixed built-in commands executed deterministically (e.g. `/help`, `/compact`, `/model`), and skill-backed commands that load prompt content into context (e.g. `/debug`, `/code-review`). The older `.claude/commands/*.md` format (filename → `/name`) still works and is functionally folded into the skills system — "Custom commands have been merged into skills."

[Source: https://code.claude.com/docs/en/slash-commands] Naming/namespacing: personal/project skills use their directory name; nested directory skills get a path-qualified alias (`/apps/web:deploy`) on name clash; plugin skills are namespaced `/plugin-name:skill-name` (bare name also works if unambiguous). Precedence on name collision: Enterprise > Personal > Project skills > Bundled; local skill > synced (claude.ai) skill of the same name.

[Source: https://code.claude.com/docs/en/mcp] MCP server "prompts" are also surfaced as slash commands automatically, `/mcp__<server>__<prompt>`, appearing/disappearing as servers connect/disconnect.

---

## 10. MCP support (Claude Code as MCP client)

[Source: https://code.claude.com/docs/en/mcp] Claude Code is a full MCP client. Config lives in `.mcp.json` (project root, VCS-shared) and `~/.claude.json` (user/local, private), under an `mcpServers` object keyed by server name, each entry specifying `type` (`http`, `sse` [deprecated], `ws`, `stdio`), `command`/`args`/`env` (stdio) or `url`/`headers` (remote), plus optional `timeout`, `headersHelper` (custom auth), and `oauth` blocks. Environment-variable expansion (`${VAR}`, `${VAR:-default}`) and Claude-specific placeholders (`${CLAUDE_PROJECT_DIR}`, `${CLAUDE_PLUGIN_ROOT}`, `${CLAUDE_PLUGIN_DATA}`) are supported in these fields.

[Source: https://code.claude.com/docs/en/mcp] Scopes and precedence (highest first): Local (`~/.claude.json`, per-project entry, private) > Project (`.mcp.json`, shared) > User (`~/.claude.json`, global) > plugin-provided servers > claude.ai connectors. Project-scoped and local-scope servers require workspace trust before first use. Managed via `claude mcp add/add-json/list/get/remove/login/logout`, and interactively via `/mcp`.

[Source: https://code.claude.com/docs/en/mcp] Claude Code discovers tools, resources, and prompts from each connected server (standard MCP capability negotiation). Tool schemas can stay deferred and be loaded on demand via tool search (`ENABLE_TOOL_SEARCH`) to save context. Output size is capped (default warning at 10,000 tokens, hard default 25,000, configurable via `MAX_MCP_OUTPUT_TOKENS`; a server can raise its own per-tool ceiling via `_meta["anthropic/maxResultSizeChars"]`, up to 500,000 chars).

[Source: https://code.claude.com/docs/en/mcp] Claude Code can also **run as an MCP server itself** (`claude mcp serve`), exposing its own capabilities (stdio transport) to other MCP clients such as Claude Desktop.

---

## 11. Configuration (settings.json / settings.local.json / hierarchy)

Covered in depth in Section 2. Summary of the five-level stack (highest to lowest): Managed → command-line (`--settings`) → project local (`.claude/settings.local.json`) → shared project (`.claude/settings.json`) → user (`~/.claude/settings.json`). [Source: https://code.claude.com/docs/en/settings]

[Source: https://code.claude.com/docs/en/settings-reference] Settings cover: model selection/fallback, permission rules and modes, MCP server allow/deny lists, plugin/skill enable-disable (`skillOverrides`, `disableBundledSkills`), auth/provider routing (`forceLoginMethod`, `apiKeyHelper`, cloud-credential helpers), hooks configuration/allowlists, sandbox filesystem/network/credential isolation, remote/desktop features, git attribution, interface/terminal behavior, and version pinning. `$schema` pointing at a published JSON Schema (`https://json.schemastore.org/claude-code-settings.json`) gives editor-level autocomplete/validation.

[Source: https://code.claude.com/docs/en/settings] Claude Code watches settings files and hot-reloads most keys mid-session (permissions, hooks, credential helpers); a few keys (e.g. `requiredMinimumVersion`) only take effect on restart. Cloud sessions (Claude Code on the web) only read shared project settings + server-managed settings — not user/local files, which stay on the originating machine.

---

## 12. Reusable instructions (sharing instructions across projects)

[Source: https://code.claude.com/docs/en/memory] Mechanisms for cross-project reuse: (a) user-level `~/.claude/CLAUDE.md` and `~/.claude/rules/` (apply to every project on the machine); (b) symlinking `.claude/rules/` entries to a shared external directory (`ln -s ~/shared-claude-rules .claude/rules/shared`); (c) `@path` imports, including importing a file from the home directory to share instructions across git worktrees of the same repo; (d) org-wide managed-policy `CLAUDE.md` deployed via MDM/config-management to every machine.

[Source: https://code.claude.com/docs/en/skills] Skills are the reusable-workflow analog: personal skills (`~/.claude/skills/`) apply across all local projects; plugins package skills/agents/hooks/MCP servers for distribution as an installable unit; skills can also be synced from a claude.ai account into Cowork/cloud sessions.

[Source: https://code.claude.com/docs/en/sub-agents] Subagent definitions follow the same personal (`~/.claude/agents/`) vs. project (`.claude/agents/`) vs. plugin split as skills, giving another reuse path for delegation patterns specifically.

**Not documented / could not verify**: a first-class "package registry" for CLAUDE.md content itself (as opposed to skills/plugins) — reuse of raw instructions appears to rely on imports/symlinks/managed policy rather than a distribution mechanism of its own.

---

## 13. Capability discovery

[Source: https://code.claude.com/docs/en/skills, https://code.claude.com/docs/en/slash-commands] Users/Claude discover available capabilities primarily via: `/skills` (lists available skills + descriptions), `/help` (built-in command reference), `/agents` (implied by subagent management, not directly confirmed in fetched pages — see caveat below), `/mcp` (lists/manages connected MCP servers and their tools), `/permissions` (lists all active permission rules and which settings file each came from), `/hooks` (browse configured hooks/matchers/handlers), `/context` (shows what's actually loaded in the current session, including which CLAUDE.md/memory files loaded), `/status` (which settings sources are active), `claude doctor` (resolved-settings diagnostics, rejected entries).

[Source: https://code.claude.com/docs/en/context-window] At the model level, capability discovery is front-loaded into the system prompt/startup context: MCP tool names (schemas deferred), skill one-line descriptions, and the tool set itself are all listed before the first user turn, so Claude "knows" what's available without a separate discovery call in the common case. `ToolSearch`/`WaitForMcpServers` tools exist specifically to let Claude pull in a deferred tool's full schema on demand rather than loading everything upfront.

[Source: https://code.claude.com/docs/en/skills] `/skill-doctor` (v2.1.252+) reports per-skill cost (context/tokens) and usage frequency, functioning as a capability-audit tool for skills specifically.

**Caveat**: the exact command name for listing/managing subagents (e.g. whether it's `/agents`) was referenced indirectly in secondary sources but not confirmed by direct fetch of an official page in this research pass — treat as **not fully verified**, though subagent listing functionality clearly exists via `/permissions` (Agent rules) and the `Agent`/`ListAgents`/`SendMessage` tools.

---

## 14. Agent-specific limitations (explicitly documented constraints)

[Source: https://code.claude.com/docs/en/tools-reference] Per-tool documented constraints include: `Bash` 2-minute default timeout and 5GB output cap, no env-var persistence between calls; `Glob` results capped at 100 files; `TaskCreate/Get/List/Update` **not available by default** on Opus 4.8+, Sonnet 5, Fable 5, Mythos 5 (opt-in only); `Monitor`, `SendUserFile`, `PushNotification`, `SendFeedback`, `RemoteTrigger` not available on Bedrock, Google Cloud Agent Platform, or Microsoft Foundry; `EndConversation` requires specific model tiers and an interactive terminal, unavailable to subagents, Bedrock, or bare mode; `Artifact`, `RemoteTrigger`, `ShareOnboardingGuide` require a Pro/Max/Team/Enterprise plan.

[Source: https://code.claude.com/docs/en/permissions] Explicitly documented as **fragile/unsafe**: Bash permission rules that try to constrain arguments (e.g. restricting `curl` to a domain) are documented as bypassable via redirects, protocol changes, variable indirection, etc. — the docs recommend deny-listing the Bash tool and relying on `WebFetch(domain:...)` or PreToolUse hooks instead. `bypassPermissions` mode is explicitly flagged: "Only use this mode in isolated environments like containers or VMs where Claude Code can't cause damage."

[Source: https://code.claude.com/docs/en/memory] CLAUDE.md and auto memory are explicitly **not enforced configuration** — Claude can deviate from them; only permission rules and hooks are hard enforcement. This is stated directly in the docs, not inferred.

[Source: https://code.claude.com/docs/en/mcp] WebSocket-transport MCP servers only support OAuth via `headersHelper`, not `--header`; `claude mcp add --transport ws` is not supported (must use `add-json`).

[Source: https://github.com/anthropics/claude-code] The GitHub repo README did not surface an explicit "known limitations" section in this pass; the repo shows a large number of open issues (5,000+) and active PR volume, consistent with a fast-moving product, but no canonical limitations list was found there — the settings/tools/permissions docs pages (cited above) are the more authoritative source for hard constraints.

**Not documented / could not verify**: any hard cap on total repository size Claude Code can "understand" beyond per-tool limits (Glob's 100-file cap, per-file token/size ceilings for Read); official docs frame this as a context-budget problem rather than stating a fixed max repo size.

---

## Preliminary cross-ecosystem notes (to be reconciled in the comparison doc)

**Note: everything in this section is explicitly preliminary and my own synthesis, not sourced from official docs elsewhere. It is offered to seed the later comparison/schema work, not as a conclusion.**

1. **Likely universal across coding agents** [Inference, not confirmed in docs]:
   - A markdown "project instructions" file loaded at session start (Claude Code: CLAUDE.md; almost certainly has direct analogs — AGENTS.md is explicitly named in Claude Code's own docs as a format other tools use).
   - Some notion of "skills"/"custom commands"/"prompts" packaged as reusable, invokable units with a description used for auto-triggering.
   - A permission/approval layer gating shell execution and file writes, with an allow/ask/deny style model and some notion of "approve once" vs. "approve permanently."
   - MCP-client behavior — MCP is an open, cross-vendor protocol, so any MCP-supporting agent will have broadly similar server-scoping and tool/resource/prompt discovery concepts.
   - Context-window management via summarization/compaction once a session runs long.
   - Sub-task delegation to a narrower-context worker (even if not called "subagents" everywhere).

2. **Distinctly Claude-Code-specific / vendor-specific** [Inference, not confirmed in docs]:
   - The specific frontmatter surface of SKILL.md (`context: fork`, `agent:`, `background:`, `disable-model-invocation`, `argument-hint`, the `$ARGUMENTS`/`$0`/`${CLAUDE_*}` substitution vocabulary, dynamic `!`command`` injection) — this is a rich, Claude-Code-specific superset layered on top of the more minimal "Agent Skills open standard."
   - Auto memory as a second, model-authored memory channel distinct from and complementary to the human-authored instructions file, with its own typed schema (`user`/`feedback`/`project`/`reference`) and size-capped index file.
   - The five-tier settings precedence stack with the specific managed/command-line/local/project/user ordering and the small list of "stricter value always wins" security exceptions.
   - Fork-mode subagents that inherit the *entire* parent conversation verbatim (as opposed to a fresh subagent context) — a fairly distinctive design choice.
   - The five hook *handler types* (command/http/mcp_tool/prompt/agent) and the very large, granular lifecycle-event taxonomy (30+ named events).
   - Bundled skills (`/run`, `/verify`, `/doctor`, etc.) as product-specific defaults.
   - Plan mode, worktree-isolated subagents, and the specific `Agent(param:value)` permission-matching syntax.

3. **What seems like it should inform a vendor-neutral "core" skill schema** [Inference, not confirmed in docs]:
   - Minimal required fields: a name/identifier, a natural-language `description` used for matching/triggering, and a body of instructions — this minimal core is explicitly what Claude Code says the "Agent Skills open standard" covers, with everything else (tool scoping, subagent execution, dynamic injection) as vendor extensions.
   - A clean separation between "reference knowledge" (always-available context) and "task/workflow" (invoked on demand, possibly with side effects) — Claude Code's own docs draw exactly this distinction between CLAUDE.md/rules (context) vs. skills (invoked workflows) vs. hooks (enforced automation).
   - Explicit invocation-control semantics (who can trigger: user only / model only / both) seem like a generally useful axis other agents likely need too, even if implemented differently.
   - A portable way to express "this skill needs these tools" (allow/deny tool scoping) independent of any one agent's actual tool names — this will be one of the harder things to make vendor-neutral, since tool names/capabilities differ per agent.
   - The three-way distinction Claude Code draws between "instructions" (soft, model-followed), "hooks" (hard, enforced regardless of model behavior), and "permissions" (hard, gate specific actions) is a useful conceptual split for a vendor-neutral spec to preserve, since it maps to a real reliability distinction, not just a Claude Code quirk.

4. **What would need a Claude-Code-specific adapter** [Inference, not confirmed in docs]:
   - Translating a generic skill's tool-access declarations into Claude Code's `allowed-tools`/`disallowed-tools` syntax and its specific tool-name vocabulary (`Bash`, `Read`, `Edit`, `mcp__server__tool`, etc.).
   - Mapping a generic "run this in isolation" concept onto Claude Code's specific `context: fork` + `agent:` + `background:` subagent machinery, including its foreground/background tool-set restrictions.
   - Mapping generic lifecycle hooks (e.g. "before file write," "after task complete") onto Claude Code's specific named events (`PreToolUse` with a `matcher`, `PostToolUse`, etc.) and its five handler types.
   - Any generic "variable substitution" syntax would need translating into Claude Code's `$ARGUMENTS`/`$name`/`${CLAUDE_*}` placeholders.
   - Settings/permission precedence rules are Claude-Code-specific enough (five-tier stack, deny>ask>allow ordering, merge-vs-replace-by-key rules) that a generic "who can configure this" concept would need a nontrivial mapping layer.
   - Memory: a generic "let the agent remember things across sessions" capability would need mapping onto Claude Code's specific `MEMORY.md` index + topic-file structure and its 200-line/25KB read-limit behavior.

5. **What should NOT be assumed to hold for other agents** [Inference, not confirmed in docs]:
   - That every agent has two separate memory channels (human-authored instructions + model-authored auto memory) — this Claude Code auto-memory feature seems like a differentiator, not a baseline other agents can be assumed to already have.
   - That skills can run in an isolated forked subagent that inherits full conversation history — many simpler agents' "skill"/"tool" mechanisms likely execute in the current context only, with no subagent concept at all.
   - That permission enforcement happens at a client layer fully independent of the model, with a formal deny>ask>allow rule grammar as rich as Claude Code's (wildcard command matching, gitignore-style path patterns, compound-command parsing, wrapper-stripping) — many agents may have much simpler or purely model-mediated permission behavior.
   - That there's a five-level settings precedence hierarchy with managed/enterprise policy as a distinct, unoverridable tier — smaller or non-enterprise-focused agents may have only one or two configuration scopes (e.g., just "project" and "user"), or none at all.
   - That MCP is supported at all — while MCP is an open standard, not every coding agent implements it as a client, and even among those that do, transport support (stdio/HTTP/SSE/WebSocket) and OAuth handling vary.
   - That "skills," "subagents," "hooks," and "slash commands" are four cleanly distinct concepts — Claude Code itself documents these as increasingly merged (custom commands "merged into skills"; hooks embeddable inside skill/subagent frontmatter), so other agents may split these boundaries very differently, or not have some of them as separate concepts at all.
