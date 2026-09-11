# Windsurf Research (as of 2026-09-09)

## IMPORTANT CONTEXT: Windsurf → Devin Desktop rebrand

[Source: https://docs.windsurf.com/windsurf/cascade/memories (307-redirects to https://docs.devin.ai/desktop/cascade/memories)] As of today, **every page under `docs.windsurf.com/windsurf/...` and `docs.windsurf.com/context-awareness/...` returns an HTTP 307 redirect to the equivalent page under `docs.devin.ai/desktop/...`.** The "Windsurf" documentation domain no longer hosts its own content — it forwards to Cognition's Devin documentation.

[Source: WebSearch result citing https://www.digitalapplied.com/blog/windsurf-becomes-devin-desktop-ide-migration-2026 and https://news.creeta.com/en/windsurf-renamed-devin-desktop-2026/ — third-party, not official, but corroborated by the doc redirects themselves] Cognition (maker of Devin) acquired Windsurf around July 2025, and on **June 2, 2026** published "Windsurf Is Now Devin Desktop," rebranding the product. Existing users received the change automatically on restart, keeping their account/plan/extensions/keybindings.

[Source: https://docs.devin.ai/desktop/devin-local] The rebrand came with a new local agent, **"Devin Local,"** a Rust rewrite of the old Python **"Cascade"** agent, described as "our next-generation agent harness shared with Devin CLI." **Cascade is not fully removed** — new tabs default to Devin Local when available, falling back to Cascade otherwise, and admins can disable Cascade via `devin.cascade.enabled`. Windsurf still appears as legacy naming throughout: directory paths like `.windsurf/`, `~/.codeium/windsurf/`, config keys like `windsurf.cascadeCommandsAllowList`, and files like `.windsurfrules`/`.windsurfignore` are all still read as fallbacks.

**Implication for this research:** the "Windsurf" ecosystem today is really two overlapping agent runtimes inside one IDE (now called Devin Desktop): the legacy **Cascade** agent (original Windsurf design, being phased out) and the newer **Devin Local** agent (default going forward). Below, findings are labeled by which agent they apply to wherever docs distinguish them. Where a doc URL still lives under a `windsurf/...` path (pre-redirect) I cite the original URL and note the redirect target.

---

## Skills

[Source: https://docs.devin.ai/desktop/cascade/skills (redirect target of https://docs.windsurf.com/windsurf/cascade/skills)] Cascade has a **"Skills"** feature: bundles of instructions plus supporting files (scripts, templates, checklists) for complex multi-step tasks.
- Uses **progressive disclosure**: Cascade initially only sees a skill's `name` and `description`; the full `SKILL.md` and supporting files load only when Cascade decides to invoke the skill, or when the user explicitly `@mentions` it.
- File format: a `SKILL.md` with YAML frontmatter (`name`, `description`) plus markdown body; supporting files (scripts, templates) live alongside it in the same directory.
- Locations:
  - Workspace (committed to repo): `.windsurf/skills/<skill-name>/`
  - Global (all workspaces, not committed): `~/.codeium/windsurf/skills/<skill-name>/`
  - System (enterprise, read-only): `/Library/Application Support/Windsurf/skills/` (macOS), `/etc/windsurf/skills/` (Linux/WSL), `C:\ProgramData\Windsurf\skills\` (Windows)
- Activation: automatic (Cascade matches request against skill descriptions) or manual (`@skill-name`).
- Creation: via Cascade panel "Customizations" menu, or by hand-authoring the directory/file structure.
- Docs explicitly position Skills vs. Rules vs. Workflows vs. Memories in a comparison table: Skills = multi-step procedures + supporting files, invoked automatically or by @mention, minimal context cost until invoked.

[Source: https://docs.devin.ai/desktop/devin-local] Devin Local (the newer agent) also **supports Skills** ("reusable instruction bundles") — listed explicitly under "Supported" features, alongside rules, AGENTS.md, worktree sessions, Plan mode, and MCP servers.

## Rules / project instructions / user instructions

[Source: WebSearch result summarizing docs.devin.ai desktop cascade rules content, corroborated by the memories/AGENTS.md fetches below] As of Sept 2026 the rule-file hierarchy is:
- `global_rules.md` — global, always-on, 6,000-character cap.
- `.devin/rules/*.md` — the new preferred workspace-rule location.
- `.windsurf/rules/*.md` and the single legacy `.windsurfrules` file — still read as fallbacks, 12,000 characters per file.
- `AGENTS.md` — auto-detected and fed into the same rules engine (see below).

[Source: https://docs.devin.ai/desktop/cascade/agents-md (redirect target of https://docs.windsurf.com/windsurf/cascade/agents-md)] **AGENTS.md** support: Devin Desktop auto-discovers `AGENTS.md`/`agents.md` (case-insensitive) files throughout the workspace and parent directories up to the git root, with no special frontmatter required.
- An `AGENTS.md` at the **root** is treated as an **always-on rule** — its full content is included in the system prompt on every message.
- An `AGENTS.md` in a **subdirectory** becomes a **glob rule** matching `<directory>/**`, activating only when Cascade reads/edits files in that directory.
- AGENTS.md is positioned as suited to "simple, location-based conventions," while the Rules system (`.devin/rules/`) is for "cross-cutting concerns and complex activation logic."

[Source: WebSearch summary of docs.devin.ai desktop cascade rules] Rule **activation modes** are: always-on, manual, model-decision, and glob/path-based — mirroring what community sources describe as parallel to older ".windsurfrules" behavior.

[Inference, not confirmed in docs] Given the AGENTS.md and Skills docs both explicitly compare themselves against "Rules," it's likely Rules remain the single umbrella mechanism into which AGENTS.md content, `.windsurfrules`, and `.devin/rules/*.md` are all normalized at runtime — but I could not fetch the dedicated `.../cascade/rules` page directly (it 404'd for me), so the precise on-disk precedence order between `.devin/rules/`, `.windsurf/rules/`, and `.windsurfrules` when several exist simultaneously is **not documented / could not verify** from primary sources in this session.

## Context and context loading

[Source: https://docs.devin.ai/desktop/context-awareness/overview (redirect target of https://docs.windsurf.com/context-awareness/overview)] Context is assembled from:
- Active/open files in the IDE.
- The **entire local codebase**, indexed and retrieved via RAG ("retrieval-augmented generation") using a proprietary technique the docs call **"M-Query"**, rather than fine-tuning a model on the code.
- Remote repositories (Teams/Enterprise only, see Remote Indexing below).
- **Context pinning**: users can pin specific items (module definitions, framework examples, interface specs, focus directories, test files) to boost their relevance; docs warn "pinning too much may slow down or negatively impact model performance."
- **@-mentions**: a chat-specific mechanism to reference codebase context directly in a Cascade/Chat conversation.
- Limits vary by plan: Pro gets "expanded context lengths, increased indexing limits, higher custom/pinned context caps."
- **Knowledge Base (Beta)**, Teams/Enterprise only: up to 50 Google Docs can be pinned as shared team context, accessible to all members regardless of individual Drive permissions.

[Source: https://docs.windsurf.com/context-awareness/fast-context.md → title only, page not independently fetched in full] "Fast Context" retrieves relevant code from the codebase "up to 20x faster using SWE-grep models" — mentioned in the docs' own page description; full page content not independently verified beyond this title/description string.

[Source: WebSearch summary, general] Windsurf's context engine indexes the entire local codebase (not just open files) into vector embeddings; one third-party source claims a **10,000-file cap** for local indexing due to RAM limits — **this specific numeric cap was not independently confirmed on an official page I could fetch**, so treat it as unverified/possibly outdated.

## Tools and tool calling

[Source: https://docs.devin.ai/desktop/cascade/cascade (redirect target of https://docs.windsurf.com/windsurf/cascade/cascade)] Cascade's built-in tools include: web search, code search/analysis, integrated terminal, automatic package detection/installation, file read/modify (respecting `.codeiumignore`), and MCP server tools. Cascade also runs a **separate planning sub-model** that "continuously refines the long-term plan" while the selected model executes short-term actions, auto-generating Todo lists for complex tasks.
- **Tool call limit**: Cascade can make up to **20 tool calls per prompt**; hitting the limit requires the user to press "continue" (which consumes additional prompt credits).
- **Modes** gate tool availability: **Code Mode** (aka Write) allows full file creation/edits + terminal; **Plan Mode** explores/asks questions/produces a saved plan without executing; **Ask/Chat Mode** is read-only, for Q&A/research only.
[Source: https://docs.devin.ai/desktop/cascade/modes] Confirms three modes — Code (default, fully agentic), Plan (saved as persistent Markdown plans under `~/.windsurf/plans` or `~/.devin/plans`, supports "megaplan"/"ultraplan" trigger keywords for deeper planning), and Ask (read-only research mode). Switch via the mode selector UI or `⌘+.`/`Ctrl+.`.

**Permission/approval model — Cascade (legacy):**
[Source: https://docs.devin.ai/desktop/terminal] Command execution has four auto-execution tiers, configured in settings:
1. **Disabled** — all commands need manual approval.
2. **Allowlist Only** — only allowlisted commands auto-run.
3. **Auto** — model judges safety per-command; risky commands still prompt; premium-models only.
4. **Turbo** — everything auto-executes except denylisted commands.
Allow/deny lists are configured via `windsurf.cascadeCommandsAllowList` / `windsurf.cascadeCommandsDenyList`; **deny always overrides allow** if a command matches both. Enterprise admins can cap the max auto-execution level org-wide and merge in team-wide allow/deny lists.

**Permission/approval model — Devin Local (newer agent):**
[Source: https://docs.devin.ai/desktop/devin-local] Replaces the auto-execution tiers with a granular **Deny / Ask / Allow rules** system scoped independently to file reads, file writes, command execution, HTTP fetches, and MCP tool calls.
[Source: WebSearch summary of https://docs.devin.ai/cli/reference/permissions] Rule evaluation order is strict priority: **Deny is checked first and wins outright; Ask is checked second (always prompts, overriding any Allow match); Allow only applies if nothing else matched.**
[Source: https://docs.devin.ai/desktop/devin-local] Devin Local also adds **OS-level sandboxing**: filesystem isolation scoped by permission, and network filtering via domain allow/deny lists. Also notes "MCP tools require explicit approval by default" under Devin Local, differing from Cascade.

## File access and repository understanding (codebase indexing)

[Source: https://docs.devin.ai/desktop/context-awareness/overview] Local codebase is indexed automatically on open; retrieval is RAG-based via embeddings, not full-file inclusion or fine-tuning.

[Source: https://docs.devin.ai/desktop/context-awareness/windsurf-ignore (redirect target of https://docs.windsurf.com/context-awareness/windsurf-ignore)] Ignore-file mechanism supports three filenames simultaneously: `.devinignore` (primary), `.codeiumignore` (legacy), `.windsurfignore` (file access) — all gitignore-style syntax, all can coexist.
- Repo-root ignore files are workspace-scoped; enterprise-wide rules can be placed at `~/.codeium/` for global enforcement across all repos.
- Without any ignore file, default exclusions are: paths in `.gitignore`, `node_modules`, and dotfiles/dot-directories.
- Ignored files are excluded from indexing **and** don't count against the "Indexing Max Workspace Size" file-count cap.
- Files matched by `.gitignore` specifically **cannot be edited by the agent** at all (not just excluded from indexing/context).

[Source: https://docs.devin.ai/desktop/context-awareness/remote-indexing (redirect target of https://docs.windsurf.com/context-awareness/remote-indexing)] **Remote indexing** (Teams/Enterprise only, requires "Devin Desktop Plugins"): indexes GitHub/GitLab/Bitbucket repos without storing code locally — repo is cloned and embedded server-side in an "isolated tenant," original code deleted afterward unless "Store Snippets" is enabled; no sharing of indexing data across different Teams customers. Configured via `https://windsurf.com/indexing` (branch selection, re-index interval).

## Memory

[Source: https://docs.devin.ai/desktop/cascade/memories (redirect target of https://docs.windsurf.com/windsurf/cascade/memories)] **Cascade Memories** (legacy agent only):
- **Auto-generated**: Cascade creates memories automatically when it "encounters context that it believes is useful to remember"; users can also explicitly ask it to "create a memory of...".
- **Storage/scope**: stored locally per-workspace at `~/.codeium/windsurf/memories/`; a memory created in one workspace is **not** available in another, and memories are **not committed to the repo** (i.e., not team-shared by default).
- **Retrieval**: model-driven — Cascade decides when a stored memory is relevant; not a rule-based trigger.
- **Cost**: creating/using auto-generated memories does **not** consume credits.
- **Team sharing**: docs explicitly recommend that durable, team-shareable knowledge be written to a **Rule** (`.devin/rules/`) or to `AGENTS.md` instead of relying on Memories.
- **Critical limitation**: *"Memories apply to the legacy Cascade agent only. The Devin Local agent — the default agent for new tabs — does not persist memories."* Docs recommend migrating relied-upon memories to Skills via a "Migration Wizard" command.
- Managed via the "Customizations" icon in Cascade's UI, or "Devin - Settings."

[Source: https://docs.devin.ai/desktop/devin-local] Confirms Memories are explicitly listed under "Unsupported" for Devin Local, alongside Workflows, Code Lenses, App Deploys, Conversation Sharing, and Arena Mode.

## Sub-agents and delegation

[Source: https://docs.devin.ai/desktop/devin-local] Devin Local can **spawn independent subagents** to handle subtasks, either in the **foreground or background**. Subagents share tools and codebase context with the parent agent but run in their own separate conversation/session chain.
- Custom subagents can be defined as markdown files under an `agents/` directory using either:
  - Flat file: `agents/<name>.md` (filename = subagent identifier), or
  - Directory: `agents/<name>/AGENT.md` (directory name = identifier).
- Gated behind a **"Subagents (Preview)"** toggle in Devin Settings — i.e., still a preview/beta feature.
- Docs frame this as mirroring the multi-agent architecture "Devin Cloud" already used, i.e. bringing cloud-Devin's orchestration pattern down into the local/desktop agent.

[Source: https://docs.devin.ai/desktop/cascade/cascade] By contrast, the legacy Cascade agent's only "multi-agent-like" behavior documented is an internal **planning sub-model** that refines a long-term plan while the main model executes — this is an internal implementation detail, not a user-facing delegation mechanism, and is architecturally different from Devin Local's user-definable subagents.

## Hooks

[Source: https://docs.devin.ai/desktop/cascade/hooks (redirect target of https://docs.windsurf.com/windsurf/cascade/hooks)] Cascade Hooks let you run shell commands at lifecycle points, with **12 documented hook events**:
- Pre-hooks (can block by exiting with code 2): `pre_read_code`, `pre_write_code`, `pre_run_command`, `pre_mcp_tool_use`, `pre_user_prompt`.
- Post-hooks (logging/monitoring only, cannot block): `post_read_code`, `post_write_code`, `post_run_command`, `post_mcp_tool_use`, `post_cascade_response`, `post_cascade_response_with_transcript` (full JSONL transcript), `post_setup_worktree`.
- **Config format** (JSON): each hook entry has `command` (bash -c on macOS/Linux), `powershell` (Windows), `show_output` (bool), `working_directory`.
- **File locations**, three-level hierarchy that merges: System (`/Library/Application Support/Windsurf/hooks.json` macOS, `/etc/windsurf/hooks.json` Linux/WSL, `C:\ProgramData\Windsurf\hooks.json` Windows), User (`~/.codeium/windsurf/hooks.json` desktop, `~/.codeium/hooks.json` JetBrains plugin), Workspace (`.windsurf/hooks.json`, version-controlled).
- **Input**: hooks receive JSON on stdin with `agent_action_name`, `trajectory_id`, `execution_id`, `timestamp`, `model_name`, `tool_info`.
- **Exit codes**: `0` success/proceed; `2` blocks the action (pre-hooks only) and shows stderr to the user; other codes = error but action proceeds anyway.
- **Limitations**: hooks don't run in "Restricted Mode"; only pre-hooks can block; hooks run with full user account privileges (docs explicitly warn poorly-designed/malicious hooks can modify files, delete data, expose credentials); recommended to target sub-100ms execution for responsiveness.
- **Enterprise distribution**: admins configure via a cloud dashboard (Enterprise plan) or push system-level hooks.json via MDM (Jamf, Intune) / config management (Ansible, Puppet, Chef).

[Inference, not confirmed in docs] Whether Devin Local supports the same Hooks mechanism (vs. only Cascade) was not explicitly confirmed — the Hooks doc page I fetched is nested under `windsurf/cascade/`, suggesting it may be Cascade-specific, but the Devin Local "Supported/Unsupported" list I fetched did not mention Hooks either way. **Not documented / could not verify** whether Hooks apply to Devin Local.

## Commands (custom workflows, slash commands)

[Source: https://docs.devin.ai/desktop/cascade/workflows (redirect target of https://docs.windsurf.com/windsurf/cascade/workflows)] **Workflows** (Cascade legacy feature):
- Stored as markdown files in `.windsurf/workflows/` (workspace) or `~/.codeium/windsurf/global_workflows/` (global/personal); each file capped at **12,000 characters**; each has a title, description, and sequential steps.
- Invoked via slash command `/[workflow-name]`; **manual-only** — "Cascade will never invoke a workflow automatically."
- Workflows can call other workflows (composable, e.g. `/workflow-1` invoking `/workflow-2`).
- Cascade can auto-generate a workflow file from a user's natural-language request.
- Discovery is hierarchical across workspace, git repo structure, and global storage; when multiple folders are open, duplicate-named workflows are deduped and shown by shortest relative path.
- Enterprise: system-level workflows can be centrally administered.
- **Explicitly listed under "Unsupported" for Devin Local** [Source: https://docs.devin.ai/desktop/devin-local]: *"The Devin Local agent does not support them."*

## MCP support

[Source: https://docs.devin.ai/desktop/cascade/mcp (redirect target of https://docs.windsurf.com/windsurf/cascade/mcp)]
- **Config file**: `~/.codeium/windsurf/mcp_config.json` (macOS/Linux); `%USERPROFILE%\.codeium\windsurf\mcp_config.json` (Windows). JSON with a top-level `mcpServers` object keyed by server name (case-sensitive). Supports variable interpolation: `${env:VAR_NAME}` and `${file:/path/to/file}`.
- **Transports**: stdio, Streamable HTTP, and SSE. HTTP-based servers configure via `serverUrl`/`url`. OAuth supported per-transport.
- **Adding servers**: via MCP Marketplace (UI, "MCPs" icon), Devin Settings UI, direct JSON editing, or one-click deeplinks (`windsurf://windsurf-mcp-registry?serverName=<server-name>`). Official/verified MCPs show a blue checkmark.
- **Live reload**: editing the config file takes effect without restarting the IDE — it watches the file and restarts context-server processes on change.
- **Tool call cap**: Cascade allows **at most 100 total tools** accessible at any given time (across all connected MCP servers combined); individual tools can be toggled per-MCP.
- **Governance**: Team admins can globally enable/disable MCP, configure a custom MCP registry, or maintain a regex-based server allowlist — once any server is allowlisted, all non-allowlisted servers are blocked org-wide.
- **Safety notes**: PostgreSQL MCP servers default to read-only "for safety"; docs explicitly disclaim liability for MCP tool call failures since server implementations are arbitrary third-party code.
- Under **Devin Local**, [Source: https://docs.devin.ai/desktop/devin-local] MCP servers remain supported, but "MCP tools require explicit approval by default," and configuration is managed via `config.json` files rather than UI-only settings — a change from Cascade's model.

## Configuration (`.windsurf/` directory structure, settings hierarchy)

Synthesizing the directory paths confirmed across the above sections:
- `.windsurf/skills/<name>/SKILL.md` — workspace skills [Source: docs.devin.ai/desktop/cascade/skills]
- `.windsurf/workflows/*.md` — workspace workflows [Source: docs.devin.ai/desktop/cascade/workflows]
- `.windsurf/rules/*.md`, `.windsurfrules` — workspace rules (fallback location; `.devin/rules/*.md` is now preferred) [Source: WebSearch synthesis of docs.devin.ai/desktop/cascade/rules content]
- `.windsurf/hooks.json` — workspace hooks [Source: docs.devin.ai/desktop/cascade/hooks]
- `.windsurfignore` / `.devinignore` / `.codeiumignore` — ignore files [Source: docs.devin.ai/desktop/context-awareness/windsurf-ignore]
- `~/.codeium/windsurf/` — user-level home for memories, global_workflows, skills, mcp_config.json, hooks.json [Sources: multiple above]
- `~/.windsurf/plans` or `~/.devin/plans` — saved Plan-mode plans [Source: docs.devin.ai/desktop/cascade/modes]
- `agents/<name>.md` or `agents/<name>/AGENT.md` — Devin Local custom subagent definitions [Source: WebSearch synthesis, docs.devin.ai]
- System/enterprise-wide config paths (skills, hooks) live under OS-specific system directories (`/Library/Application Support/Windsurf/`, `/etc/windsurf/`, `C:\ProgramData\Windsurf\`) [Source: docs.devin.ai/desktop/cascade/skills, .../hooks]

[Inference, not confirmed in docs] The coexistence of `.windsurf/`-prefixed paths (legacy Cascade) and `.devin/`-prefixed paths (new, preferred) strongly suggests an in-progress, incomplete migration of on-disk conventions as of Sept 2026 — not a stable, finalized configuration hierarchy. Treat every path above as potentially transitional.

## Reusable instructions (sharing rules/workflows across projects/teams)

[Source: https://docs.devin.ai/desktop/cascade/agents-md, .../skills, .../workflows, .../hooks — synthesized] Windsurf/Devin Desktop offers several distinct team-sharing mechanisms rather than one:
- **Rules / AGENTS.md**: committed to the repo (`.devin/rules/`, `.windsurf/rules/`, root/subdirectory `AGENTS.md`) — the docs' explicitly recommended mechanism for durable, predictable, team-shared instructions ("Rules are the right mechanism because they are predictable and apply the same way for everyone").
- **Skills**: workspace skills committed to repo are team-shared; global skills are personal; system skills are enterprise-IT-managed and read-only for end users.
- **Workflows**: workspace workflows in `.windsurf/workflows/` are committed/team-shared; global workflows are personal; enterprise supports centrally-administered system-level workflows.
- **Hooks**: three-tier system/user/workspace hierarchy explicitly designed for enterprise-wide mandatory policy distribution via MDM/config-management tools.
- **Memories**: explicitly *not* a team-sharing mechanism — local-only, per-workspace, not committed to the repo; docs redirect users wanting shared/durable knowledge to Rules or AGENTS.md instead.

## Capability discovery (how Windsurf discovers/surfaces available tools/rules/commands)

[Source: https://docs.devin.ai/desktop/cascade/skills] For Skills: Cascade "sees" only `name`+`description` metadata for all defined skills up front (cheap, always-loaded index), and only loads full `SKILL.md` content when it decides to invoke a skill or the user @-mentions it (progressive disclosure).
[Source: https://docs.devin.ai/desktop/cascade/workflows] For Workflows: discovery is hierarchical (workspace → git repo → global), with deduplication by shortest relative path when multiple folders are open; the user discovers workflows via the `/` slash-command menu.
[Source: https://docs.devin.ai/desktop/cascade/mcp] For MCP tools: discoverable/manageable via a UI "MCPs" panel with an official-server checkmark indicator in a "Marketplace," subject to the 100-tool cap and per-tool toggles.
[Inference, not confirmed in docs] There is no single documented unified "capability manifest" endpoint/command that lists all active rules+skills+workflows+MCP tools at once; each category appears to have its own discovery UI/surface rather than one consolidated capability registry.

## Agent-specific limitations (explicitly documented constraints)

- [Source: https://docs.devin.ai/desktop/devin-local] Devin Local explicitly does **not** support: Memories, Workflows, Code Lenses, App Deploys, Conversation Sharing, Arena Mode. It *does* support Skills, Rules, AGENTS.md, worktree sessions, Plan mode, MCP servers.
- [Source: https://docs.devin.ai/desktop/cascade/cascade] Cascade caps tool calls at **20 per prompt**; continuing past the limit consumes extra credits.
- [Source: https://docs.devin.ai/desktop/cascade/mcp] Hard cap of **100 total MCP tools** active at once.
- [Source: https://docs.devin.ai/desktop/cascade/workflows] Workflow files are capped at **12,000 characters**; `global_rules.md` is capped at **6,000 characters**; other rule files at **12,000 characters** [Source: WebSearch synthesis of docs.devin.ai desktop cascade rules].
- [Source: https://docs.devin.ai/desktop/cascade/hooks] Hooks don't execute while the workspace is in "Restricted Mode"; only pre-hooks can block actions; hooks run with full user privileges (explicit security warning in docs).
- [Source: https://docs.devin.ai/desktop/context-awareness/remote-indexing] Remote indexing is Teams/Enterprise-only, requires "Devin Desktop Plugins," and is limited to GitHub/GitLab/Bitbucket.
- [Source: https://docs.devin.ai/desktop/acp-custom] The ACP (Agent Client Protocol) integration in Devin Desktop explicitly lacks support for "session modes and terminal capabilities as defined in the full ACP specification" — a documented partial-implementation gap.
- [Source: https://docs.devin.ai/desktop/cascade/mcp] Docs explicitly disclaim liability for MCP tool call failures, since MCP server implementations are arbitrary third-party code.
- [Source: https://docs.devin.ai/desktop/context-awareness/windsurf-ignore] Files matched by `.gitignore` cannot be edited by the agent at all, regardless of other ignore-file settings.
- Subagents in Devin Local are gated behind a **"Subagents (Preview)"** toggle — i.e., officially a preview/beta feature, not GA. [Source: WebSearch synthesis of docs.devin.ai]

---

# Preliminary cross-ecosystem notes (to be reconciled in the comparison doc)

*(All labeled preliminary/best-effort per instructions — not a final comparison.)*

**1. Likely-universal capabilities (other agents probably have an equivalent):**
- Rules/project-instructions files that get injected into the system prompt, with some notion of "always-on" vs. "conditionally activated" (glob/path-scoped) — this maps directly onto e.g. Claude Code's CLAUDE.md, Cursor's `.cursor/rules`, etc.
- `AGENTS.md` support specifically — this is an emerging cross-vendor standard (also adopted by other agents), so it's the single most "already vendor-neutral" artifact found here.
- Codebase indexing/RAG for context retrieval, plus some form of ignore-file (gitignore-style) to exclude paths from indexing/editing.
- A permission/approval model gating command execution and tool calls (allow/deny/ask-style), including a docs-stated principle that "deny always wins."
- MCP client support with a JSON config file keyed by server name, supporting stdio + HTTP transports — MCP itself is an open, cross-vendor protocol, so this is expected to be near-identical across agents that support it at all.
- Slash-command-style reusable prompt/workflow templates, manually invoked, stored as markdown files in the repo.
- A "read-only / plan / full-agentic" mode spectrum for constraining what the agent may do in a given session.

**2. Distinctly Windsurf/Devin-specific:**
- The specific **Skills progressive-disclosure design** (name+description always loaded, full content loaded only on invocation/@mention) — the exact mechanics (directory layout, `.windsurf/skills/`, three-tier workspace/global/system scoping) are Windsurf/Devin-specific implementation, even though "skills" as a concept may generalize.
- The **dual-agent transition state** (Cascade legacy vs. Devin Local) is unique to this moment in this vendor's history — a mid-migration artifact, not a stable design choice other agents would mirror.
- Specific numeric caps (20 tool calls/prompt for Cascade, 100 MCP tools total, 12,000/6,000-char file limits) are Windsurf/Devin-specific tuning choices.
- The **Agent Client Protocol (ACP)** as the mechanism for plugging arbitrary third-party agents into the IDE shell is a distinctive Cognition/Windsurf architectural bet (decoupling the IDE from any specific agent).
- Enterprise **remote indexing** with server-side embedding + "Store Snippets" toggle is a fairly specific productization choice.
- The `.windsurf/` vs `.devin/` path duality and legacy `.codeium/` naming is entirely idiosyncratic to this vendor's acquisition history.

**3. What should inform a vendor-neutral "core" skill schema:**
- The **progressive-disclosure metadata pattern** (lightweight `name`+`description` header, heavy body loaded lazily) seems like a strong candidate for a core schema primitive — it directly addresses context-window economy, which is a universal constraint, not a Windsurf quirk.
- A clean separation between **"always-on instructions"** (rules/AGENTS.md), **"invokable procedure bundles with assets"** (skills), and **"manually-triggered command templates"** (workflows/slash-commands) — Windsurf documents these as three genuinely distinct categories with different activation semantics, which is a useful three-way taxonomy for a core schema to preserve rather than collapse.
- Explicit **activation-mode enumeration** (always-on / manual / model-decision / glob-path) as a first-class field, since Windsurf treats this as an explicit axis of configuration.
- A notion of **scope tiers** (system/enterprise → user/global → workspace/project, with merge semantics) recurs across skills, hooks, and rules — a core schema should probably support at least workspace-vs-global scoping natively.

**4. What would need a Windsurf/Devin-specific "adapter":**
- Mapping a generic skill's assets/scripts into the exact `.windsurf/skills/<name>/SKILL.md` + sibling-files directory convention (or the newer, less-documented Devin Local equivalent).
- Translating a generic "always-on instruction" into the correct one of: root `AGENTS.md`, `global_rules.md`, `.devin/rules/*.md`, or legacy `.windsurfrules`, respecting the character caps (6,000 for global, 12,000 for workspace rules).
- Translating a generic "manual command/workflow" into Windsurf's `.windsurf/workflows/*.md` format with its 12,000-character cap and slash-command naming convention — noting this mechanism does **not exist** in Devin Local, so the adapter would need a fallback (e.g., degrade to a Skill).
- Mapping generic tool/permission declarations onto Windsurf's two different permission models depending on which agent (Cascade's four auto-execution tiers + allow/deny lists, vs. Devin Local's Deny/Ask/Allow scoped rules) is active — these are not equivalent shapes.
- Mapping a generic MCP tool manifest onto the `mcp_config.json` `mcpServers` schema and its 100-tool ceiling.

**5. What should NOT be assumed to hold for other agents:**
- The **100-total-MCP-tools cap** and **20-tool-calls-per-prompt** limit are Windsurf/Cascade-specific numbers, not evidence of a general "agents cap tool counts at ~100" norm.
- **Memories being workspace-local and explicitly non-team-shared** is a specific design choice Windsurf made (and one it's now abandoning for Devin Local, which drops memories entirely) — other agents' "memory" features may have entirely different persistence/sharing semantics (or none at all), so no default assumption about memory scope should carry over.
- The **existence of two parallel, non-interoperable agent runtimes inside one product** (Cascade vs. Devin Local) is a transitional/historical artifact of this specific acquisition and should not be treated as a generalizable "agents come in pairs" pattern.
- Windsurf's specific **Deny-beats-Ask-beats-Allow** precedence rule, while intuitive, is an implementation detail of Devin Local's permission engine — other agents may order or name these differently (or not have three discrete tiers at all).
- The **ACP protocol's specific method set** (`initialize`, `session/new`, `session/prompt`, `session/cancel`, `session/request_permission`) is one vendor's chosen open-protocol surface; it should not be assumed that other agents expose (or need) an equivalent JSON-RPC subprocess protocol for plugging in alternative agents.
