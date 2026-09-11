# Antigravity (Google) — Ecosystem Research

**Status of product identity:** Confirmed. "Google Antigravity" is a real, official Google product — an "agentic development platform" with a desktop app (Antigravity 2.0), a CLI (`agy`), a Python SDK (`google-antigravity`), and IDE extensions (VS Code, Visual Studio, JetBrains, Zed, Xcode). Official site: **antigravity.google**, official docs at **antigravity.google/docs**, official announcement/blog at **antigravity.google/blog**. This is *not* to be confused with any unrelated "Antigravity" product (e.g., game engines, hardware, or fitness brands using the same name).

There is also a related-but-distinct offering: an "Antigravity agent" exposed through Google's **Gemini API Interactions API** (`ai.google.dev/gemini-api/docs/antigravity-agent`), described as "a general-purpose managed agent on the Gemini API" that "uses the same harness as the Antigravity IDE." [Source: https://ai.google.dev/gemini-api/docs/antigravity-agent] This research focuses on the IDE/desktop/CLI/SDK product family at antigravity.google, and calls out the API variant separately where relevant.

**Caveats about sourcing:** The antigravity.google/docs site appears to be a JavaScript-rendered SPA; some individual doc URLs (e.g. `/docs/knowledge`) returned HTTP 404 to the fetch tool used for this research even though they are indexed and quoted in search results, and even though other doc pages on the same domain fetched successfully. Where a page could not be directly fetched, findings are based on search-engine-returned excerpts of that exact official page (cited with the same antigravity.google/docs URL) rather than third-party paraphrase, and this is flagged explicitly. Third-party blogs/tutorials were used only for triangulation, never as the primary citation for a claim about product behavior, and are called out as "unofficial" wherever referenced.

Product version context found in docs: Antigravity 2.0 (desktop app, v2.12.2 in docs nav), Antigravity CLI (v1.1.25), Antigravity SDK (v0.1.16), Antigravity for IDEs (v2.5.5). [Source: https://antigravity.google/docs/home/]

---

## 1. Skills

[Source: https://antigravity.google/docs/skills/] A Skill is "an open standard for extending agent capabilities." Each skill is a folder containing a required `SKILL.md` file with YAML frontmatter (`name` — optional, defaults to folder name; `description` — required, should be written in third person with keywords that help the agent recognize relevance) plus body instructions. A skill folder may also contain optional `scripts/`, `examples/`, and `resources/` subdirectories.

[Source: https://antigravity.google/docs/skills/] Two storage locations:
- Workspace-specific: `<workspace-root>/.agents/skills/<skill-folder>/`
- Global (all workspaces): `~/.gemini/config/skills/<skill-folder>/`

[Source: https://antigravity.google/docs/skills/] Discovery/invocation follows a three-stage pattern: (1) **Discovery** — the agent sees available skills' names and descriptions only; (2) **Activation** — if relevant to the task, the agent reads the full `SKILL.md` body; (3) **Execution** — the agent follows the instructions while completing the task. Explicit user mention can force activation. The docs give a "code-review" skill as a worked example.

[Source: https://antigravity.google/docs/migration/workflows-to-skills/] Skills replaced an older, now-deprecated mechanism called **Workflows** (single `.md` files under `.agents/workflows/<name>.md`) as of a platform migration adopting "the open industry standard for Agent Skills" in **May 2026**. Reasons cited: progressive/on-demand context loading ("Metadata indexed upfront; body loaded on demand") vs. full-file loading for Workflows; directory-based bundling of scripts/references/examples (not supported by Workflows); explicit claim of "ecosystem interoperability" — Skills adhere to "the cross-platform agent specification," said to enable portability across other compliant agent tools beyond Antigravity; and that the new Skill format lets a skill "define specialized system prompts, tool requirements, and delegate sub-tasks to custom subagents." Workflows are deprecated with an end-of-support/retirement date of **November 1, 2026**, with an automatic migration tool offered.

[Source: https://antigravity.google/docs/build-with-google/] Google ships curated "Build with Google" plugin bundles (Firebase, Android, Dart/Flutter, Data Agent Kit, Chrome DevTools, the Antigravity SDK itself) that bundle pre-configured Skills + MCP servers + editor extensions for specific ecosystems, enabled via `Settings > Customizations > Build with Google Plugins`.

[Source: https://antigravity.google/docs/sdk/overview/] The Python SDK also supports "Tool/skill registration and execution" and loading Skills in `SKILL.md` format programmatically.

CLI: `/skills` is a slash command surface for skills management [Source: https://antigravity.google/docs/cli/features/]; CLI docs also list a page "Plugins & Skills" [Source: https://antigravity.google/docs/cli/plugins/].

## 2. Rules / Project Instructions / User Instructions

[Source: https://antigravity.google/docs/ide/rules/] Rules are Markdown files, capped at **12,000 characters** each, used to encode "manually defined constraints for the Agent to follow." Two scopes:
- **Global Rules**: `~/.gemini/GEMINI.md`, apply across all workspaces.
- **Workspace Rules**: `.agents/rules` folder (with backward-compatible support for the older `.agent/rules` path) inside the workspace/git root.

[Source: https://antigravity.google/docs/ide/rules/] Four activation modes per rule: **Manual** (triggered via `@mention` in the agent's input box), **Always On** (applied to every operation), **Model Decision** (the model decides applicability from a natural-language description of the rule), and **Glob** (pattern match, e.g. `*.js`, `src/**/*.ts`).

[Source: https://antigravity.google/docs/ide/rules/] Rules support `@filename` references to pull in other files; relative paths resolve against the rule file's own location, absolute paths are tried directly and then relative to the workspace root. Rules are managed via a "Customizations" panel (the "…" dropdown in the agent panel), with Global vs. Workspace rule creation.

[Source: search-quoted https://antigravity.google/docs/mcp/ and other pages] There is also a distinct concept of `agent.md` files for defining **named/custom agents** — search-result summaries described Antigravity as shipping "three separate customization systems: Rules for standing instructions, custom `agent.md` files for defining named agents, and `SKILL.md` files for on-demand capabilities" — this is corroborated across multiple search snippets referencing official docs but was not independently confirmed by direct-fetching a page titled exactly this way, so treat the three-way split framing as **[Inference from converging search snippets, not independently verified by direct page fetch]**.

## 3. Context and Context Loading

[Source: https://antigravity.google/docs/home/] The desktop app and CLI run on "a shared agent harness powered by Gemini 3.8 Flash" (as of when this page was captured); [Source: WebSearch excerpt of official docs/models content] Gemini 3.8 Flash "supports a 1M token context window, 64k max output tokens, tunable thinking levels (low, medium, high), and built-in tools," and Gemini 3 Pro is described elsewhere as natively multimodal with a 1M-token window.

[Source: https://antigravity.google/docs/getting-started/] "Agents work within Projects, which define the boundaries of the folders and repositories they can access." Adding multiple folders/repos to a Project gives "full cross-repository context."

[Source: https://antigravity.google/docs/skills/ and https://antigravity.google/docs/migration/workflows-to-skills/] Skill *metadata* (name + description) is loaded/indexed up front for every conversation; the full `SKILL.md` body is only loaded into context on demand once the agent judges the skill relevant ("progressive disclosure").

[Source: https://antigravity.google/docs/artifacts/] Artifacts (implementation plans, walkthroughs, task lists, screenshots, browser recordings) are generated by the agent — chiefly during a distinct "Planning Mode" — as durable, human-reviewable context objects that persist alongside the conversation, distinct from raw tool-call output.

Not documented / could not verify (from primary sources fetched directly): the exact retrieval mechanism used to select which files enter context for a given turn (e.g., embeddings vs. keyword search vs. whole-file inclusion) is not spelled out in the docs pages actually fetched. Third-party (non-official) commentary claims Antigravity uses "the Search API, code graph, and embeddings search" and can "read your entire codebase without truncation," and separately claims it "inherits VS Code's workspace-local indexing architecture" with no cross-repo aggregation at enterprise scale — both of these are **unofficial, third-party claims** (from augmentcode.com and index.dev marketing/comparison pages), not confirmed in antigravity.google/docs, and are flagged here only to note the gap, not as fact.

## 4. Tools and Tool Calling

[Source: https://antigravity.google/docs/overview/] Agents can, per the overview: execute system commands, read/write files, conduct web searches, integrate external tools via Skills and MCP servers, manage subagents, interact with Chrome, and create artifacts/implementation plans.

[Source: https://antigravity.google/docs/permissions/] Antigravity has "a unified permission engine evaluating every sensitive operation as a resource formatted as `action(target)`." Every request resolves through three access lists with strict precedence **Deny > Ask > Allow** ("Conflicting rules are strictly evaluated in priority order"). Six scoped action types: `read_file` / `write_file` (write implies read), `read_url` / `execute_url` (passive viewing vs. interactive browser actuation), `command()` (literal prefix match or regex), `unsandboxed()` (container-escape permission), and `mcp(server/tool)` (exact tool or whole-server namespace match). All support `*` wildcarding. Defaults: workspace files default to **Allow**; non-workspace file access, terminal commands, and external/MCP tools default to **Ask** unless configured; web operations default to **Ask**.

[Source: https://antigravity.google/docs/permissions/] Ask-type operations surface as interactive "permission cards" in the editor; users can broaden the requested scope inline (e.g. `read_file(/project/file.txt)` → `read_file(/project)`) to pre-empt repeat prompts — for file/URL/MCP permissions, but explicitly **not** for terminal commands.

[Source: https://antigravity.google/docs/features/] Bounded access by default: agents are restricted to read/write inside project folders; security presets "Full machine" or "Unrestricted" widen this to the whole system. Interactive approval is required before terminal command execution by default. [Source: https://antigravity.google/docs/agent-settings/] Terminal auto-execution has three modes: **Request Review** (never auto-execute except an explicit Allow list), **Proceed in Sandbox** (auto-run inside sandbox; anything outside it needs approval), and **Always Proceed** (auto-execute except an explicit Deny list).

[Source: https://antigravity.google/docs/permissions/] Sandbox-mode permissions double as container policy: `read_file` grants populate a read-only filesystem allowlist, `write_file` grants populate read-write access, and `read_url` domains are compiled directly into the sandboxed container's outbound network allowlist (so e.g. `curl`/`npm` can reach only authorized hosts).

[Source: search-quoted https://antigravity.google/docs/permissions/ / sandbox docs] Terminal Sandbox provides OS-native (not container-based) kernel-level isolation: macOS uses Seatbelt (`sandbox-exec`); Linux uses `nsjail`. Supported on macOS and Linux only (Windows not mentioned as supported).

[Source: https://antigravity.google/docs/sdk/overview/] SDK-level "Policies" let a developer declare tool access rules programmatically, including "deny-by-default templates and argument-level predicates" — i.e., the same allow/ask/deny model is exposed as a first-class policy object in the Python SDK, not just as UI settings.

## 5. File Access and Repository Understanding

[Source: https://antigravity.google/docs/features/] Default bounded access restricts read/write to the active Project's folders; [Source: https://antigravity.google/docs/agent-settings/] more specifically, default file access is scoped to project folders plus the app's own `~/.gemini/antigravity/` data directory, explicitly to "protect your local sensitive data," with an explicit warning to enable broader non-workspace access cautiously.

[Source: https://antigravity.google/docs/getting-started/] Projects can span multiple folders/repositories simultaneously for cross-repo context; a task can run in **Local Mode** (directly in the active folders) or **New Worktree Mode** (an isolated Git worktree).

[Source: https://antigravity.google/docs/faq/] Git worktree support is called out as a new/upgraded capability: "Worktrees are now supported in version 2.0 (previously unsupported)."

Not documented / could not verify: a dedicated, officially-described indexing pipeline (chunking strategy, embedding model, refresh cadence) for repository understanding was not found on any directly-fetched official page. The CLI has a `/code-search`-style feature referenced in navigation ("Code Search" appears as a CLI command page title) but the specific target page returned HTTP 404 when fetched directly during this research, so its contents are Not documented / could not verify here.

## 6. Memory

[Source: https://antigravity.google/blog/introducing-google-antigravity] The official launch blog states the platform treats "learning as a core primitive": "Agent actions both retrieving from and contributing to a knowledge base." It gives examples of what gets captured: "useful snippets of code or derived architecture," and "the series of steps taken to successfully complete a particular subtask."

[Source: antigravity.google/docs/knowledge — page content reconstructed from search-engine-quoted excerpts of that official URL, because direct fetch of this specific page returned HTTP 404 during this research; treat as officially-sourced-but-not-directly-verified] The mechanism is called **Knowledge Items (KIs)**. At the end of each conversation, a separate **Knowledge Subagent** analyzes the conversation and distills key facts into KIs. Unlike conversation history (session-bound), KIs are described as "distilled, curated facts that persist indefinitely." KIs are said to be stored under the app's local data directory (`~/.gemini/antigravity/`, alongside Artifacts) with per-item `metadata.json` (summary, timestamps, references to the originating conversation) and an `artifacts/` subfolder of related files. KIs are automatically loaded into new conversations, and the agent is described as checking KI summaries at the start of every session "to avoid redundant work." KIs are viewable from the Agent Manager UI.

[Source: https://antigravity.google/docs/build-with-google/] Separately, the SDK's Firebase bundle etc. do not describe their own memory system — Knowledge Items appear to be the one platform-wide memory mechanism.

[Source: https://mem0.ai/blog/add-persistent-memory-to-google-antigravity-cli-with-mem0-mcp — third-party/unofficial] This third-party vendor blog explicitly states "Antigravity CLI has no persistent memory natively" and sells an MCP-based add-on (Mem0) to provide cross-session memory for the **CLI** specifically. This is in apparent tension with the official Knowledge Items mechanism described above for the desktop app/IDE — it's unclear from available sources whether Knowledge Items are a desktop-app/IDE-only feature not (yet) present in the CLI, or whether the vendor blog is simply marketing copy that overstates the gap. **[Inference, not confirmed in docs]**: the most likely reconciliation is that Knowledge Items are generated by the shared agent harness generally, but the CLI surface (or the version the vendor tested) may not surface/replay them the same way the desktop Agent Manager does — this is speculative and should not be treated as confirmed.

## 7. Sub-agents and Delegation

[Source: https://antigravity.google/docs/subagents/] Subagents are created when a parent agent calls an `invoke_subagent` tool, generating "a new concurrent session with a dedicated role and initial prompt." Three workspace options for a subagent: inherit the parent's workspace, create an isolated Git worktree, or share directory storage.

[Source: https://antigravity.google/docs/subagents/] Inheritance model: a subagent inherits the parent's *safety configuration* — "allowed terminal command prefixes, file read/write directory scopes, and sandbox settings" — but explicitly does **not** inherit conversation history; each subagent "starts with a clean slate" and uses only the model tier specified in its own configuration.

[Source: https://antigravity.google/docs/subagents/] Delegation/control: permission requests from a subagent "automatically bubble up to the main UI"; the parent retains full access to subagent workspaces including isolated worktrees, and can monitor subagent progress via dedicated panels/CLI shortcuts.

[Source: https://antigravity.google/docs/subagents/] Three pre-packaged built-in subagent types: `research` (codebase exploration), `browser` (sandboxed browser testing), and `self` (a clone of the parent agent).

[Source: https://antigravity.google/docs/subagents/] Limits: maximum **10 levels** of nested subagents ("to prevent runaway recursion or resource exhaustion"); a documented gotcha that "specifying an unmapped or misspelled tool name... may cause the subagent process to hang." Lifecycle states: Running, Idle (completed, awaiting messages), Killed (terminated, with automatic worktree cleanup).

[Source: https://antigravity.google/docs/cli/features/] In the CLI, subagents run as independent, asynchronous concurrent sessions surfaced via an `/agents` panel that shows active/completed subagents, full conversation visibility, and tool-approval workflows (with `ctrl+j` / `ctrl+k` fast-path approval shortcuts). Subagents get code search, file editing, terminal, and web-search access with permissions delegated from the main agent.

[Source: https://antigravity.google/docs/features/] A dedicated **Browser Subagent** is invocable via a `/browser` slash command, integrates with Chrome DevTools MCP, and can record webm video of its session.

[Source: https://antigravity.google/docs/sdk/overview/] The Python SDK exposes "Multi-agent systems through subagents" as a first-class programmatic concept alongside `Agent`/`LocalAgentConfig`.

## 8. Hooks

[Source: https://antigravity.google/docs/hooks/] Hooks run custom local shell scripts/commands at defined points in the agent's execution loop. Five lifecycle events: **PreToolUse** (before any tool runs — can validate/block), **PostToolUse** (after a tool completes — e.g. linting, diagnostics), **PreInvocation** (before a model call — can modify the trajectory), **PostInvocation** (immediately after a model response), and **Stop** (on execution termination — can force continuation).

[Source: https://antigravity.google/docs/hooks/] Configured via a `hooks.json` file, located at `.agents/` (workspace) or `~/.gemini/config/` (global/user-level). Structure maps a hook name to a config object: `{"enabled": true/false, "PreToolUse": [...], "PostToolUse": [...], ...}`. Each entry supports a `matcher` (regex against tool name, e.g. `run_command` or `browser_.*`) and a handler (shell command with a configurable timeout, default 30s).

[Source: https://antigravity.google/docs/hooks/] I/O contract: hooks communicate over stdin/stdout as JSON; they receive metadata (`conversationId`, `workspacePaths`, `transcriptPath`, `modelName`); response shape depends on the event — PreToolUse hooks return a permission decision, PostToolUse hooks return an empty object.

[Source: https://antigravity.google/docs/sdk/overview/ and GitHub search-excerpt of google-antigravity/antigravity-sdk-python] The SDK exposes the same lifecycle conceptually in Python: "Hooks in the Google Antigravity SDK allow users and system components to intercept, observe, and modify the behavior of the agent at various stages of its execution lifecycle," explicitly covering session, turn, tool, subagent, compaction, and interaction stages — a superset of the JSON-hooks event list, described for observability, policy enforcement, data sanitization, and interactive decision-making.

## 9. Commands

[Source: https://antigravity.google/docs/getting-started/ and https://antigravity.google/docs/cli/features/] Slash commands are a core interaction surface across the desktop app and CLI. Documented commands include: `/goal` (run to completion without intermediate check-ins), `/grill-me` (ask clarifying questions before implementing), `/schedule` (one-time or recurring task timer), `/browser` (Chrome/browser-subagent control), `/boost` ("multi-agent deep reasoning for complex bugs, race conditions, and algorithms"), `/teamwork-preview` (collaborative/multi-agent projects), `/resume`, `/rewind`, `/rename` (conversation management), `/permissions`, `/model`, `/keybindings`, `/statusline` (configuration), `/tasks`, `/skills`, `/mcp`, `/diff` (tools/monitoring), `/open`, `/usage`, `/logout` (utilities).

[Source: https://antigravity.google/docs/home/] The CLI docs list an entire "Commands" section with 12+ dedicated pages (Agents, Boost, Code Search, Credits, Diff, Permissions, Resume, Status Line, Teamwork, Window Title, Model Quotas, Voice), indicating commands are documented individually, not just as a flat list.

Not documented / could not verify: a general end-user mechanism for defining **custom** slash commands (as distinct from Skills/Rules, which are the documented extension points) was not found in the pages fetched; commands appear to be a fixed, product-defined set rather than a user-authorable layer. This should be treated as an absence-of-evidence, not a confirmed "no."

## 10. MCP Support

[Source: https://antigravity.google/docs/mcp/] Antigravity supports the Model Context Protocol as an MCP **client**: "an open standard that lets AI agents and editors securely connect to local developer tools, databases, file parsers, and external remote APIs."

[Source: https://antigravity.google/docs/mcp/] Config file: JSON with a top-level `mcpServers` object. Locations: global `~/.gemini/config/mcp_config.json`; workspace-local `.agents/mcp_config.json`. Example shape:
```json
{
  "mcpServers": {
    "server-name": { "command": "node", "args": ["/path/to/server.js"], "env": {"KEY": "value"} }
  }
}
```

[Source: https://antigravity.google/docs/mcp/] Transports: `stdio` (local process via `command`/`args`) and remote HTTP — either "Streamable HTTP" or SSE via a `serverUrl` field. Auth options: `authProviderType: "google_credentials"` (requires Application Default Credentials setup), OAuth (automatic dynamic client registration, or manual `clientId`/`clientSecret`), or custom `headers` (API tokens/bearer tokens).

[Source: https://antigravity.google/docs/mcp/] Server discovery/management UIs differ by surface: desktop app — Settings → Customizations → "Installed MCP Servers" → "Add MCP" opens an "MCP Store"; IDE extension — side panel → "MCP Servers"; CLI — `/mcp` interactive manager or direct config-file edits. The MCP Store is described as offering 46+ pre-configured servers (databases, dev tools, design tools, analytics platforms).

[Source: https://antigravity.google/docs/sdk/overview/] The SDK treats "Model Context Protocol (MCP) integration" and "connect MCP servers" as first-class, programmatically configurable capabilities.

[Source: search-quoted, official CLI troubleshooting content] A documented gotcha: one invalid/unsupported MCP server entry in the config can prevent *all* other configured MCP servers from loading.

## 11. Configuration

Configuration is split across several files/directories, consistently rooted at `~/.gemini/` for global/user scope and `.agents/` for workspace scope (with legacy `.agent/` still honored for rules):

- Global rules: `~/.gemini/GEMINI.md` [Source: https://antigravity.google/docs/ide/rules/]
- Global skills: `~/.gemini/config/skills/` [Source: https://antigravity.google/docs/skills/]
- Global MCP config: `~/.gemini/config/mcp_config.json` [Source: https://antigravity.google/docs/mcp/]
- Global hooks: `~/.gemini/config/hooks.json` / `~/.gemini/config/` [Source: https://antigravity.google/docs/hooks/]
- Global sidecar definitions: `~/.gemini/config/sidecars/` and `~/.gemini/config/plugins/<pluginName>/sidecars/`; sidecar enablement in `~/.gemini/config/config.json` [Source: https://antigravity.google/docs/sidecars/]
- App data / Knowledge Items / Artifacts: `~/.gemini/antigravity/` [Source: converging search excerpts of antigravity.google/docs/agent-settings/ and /docs/knowledge]
- Workspace rules: `.agents/rules/` (legacy `.agent/rules/`) [Source: https://antigravity.google/docs/ide/rules/]
- Workspace skills: `.agents/skills/<skill-folder>/` [Source: https://antigravity.google/docs/skills/]
- Workspace MCP config: `.agents/mcp_config.json` [Source: https://antigravity.google/docs/mcp/]
- Workspace hooks: `.agents/hooks.json` [Source: https://antigravity.google/docs/hooks/]
- CLI-specific settings: `settings.json`, controlling e.g. `enableTerminalSandbox` (default `false`) [Source: https://antigravity.google/docs/cli/features/]
- CLI plugin staging directory: `~/.gemini/antigravity-cli/plugins/`, auto-discovered [Source: https://antigravity.google/docs/cli/features/]

[Source: https://antigravity.google/docs/agent-settings/] Settings hierarchy for agent behavior is Global (application preferences) with per-Project overrides, for at least: terminal command auto-execution mode, non-workspace file access, and terminal sandbox mode. No standardized on-disk file format for these particular settings is documented — the docs describe them as managed through the application UI ("application preferences") rather than a hand-edited file.

[Source: https://antigravity.google/docs/cli/plugins/] "Plugins are namespaced bundles that can contain skills, agents, rules, MCP servers, and hooks as a single deployable unit" — i.e., Plugins are the packaging/distribution unit that bundles the other customization primitives together, not a separate primitive in their own right.

## 12. Reusable Instructions (across projects)

[Source: https://antigravity.google/docs/ide/rules/] **Global Rules** (`~/.gemini/GEMINI.md`) are the primary documented mechanism for instructions that apply across every workspace/project on a machine.
[Source: https://antigravity.google/docs/skills/] **Global Skills** (`~/.gemini/config/skills/`) are the equivalent reusable mechanism for on-demand capabilities/procedures rather than standing instructions: "Global skills work across all your projects. Use these for personal utilities or general-purpose tools you want everywhere," vs. "Workspace skills are great for project-specific workflows, like your team's deployment process or testing conventions."
[Source: https://antigravity.google/docs/cli/plugins/] **Plugins** are the distribution/sharing unit — a namespaced bundle of skills+agents+rules+MCP servers+hooks that can be installed to reproduce a whole customization set across machines/projects, staged under `~/.gemini/antigravity-cli/plugins/` for the CLI.
[Source: https://antigravity.google/docs/build-with-google/] Google's own "Build with Google" bundles are themselves examples of shareable, pre-packaged multi-primitive bundles (skills + MCP + extensions) distributed this way.

## 13. Capability Discovery

Not documented in detail as a unified mechanism on any directly-fetched page. What is documented, piecemeal:
- [Source: https://antigravity.google/docs/skills/] Skills: the agent is shown *only* name+description metadata for all skills up front every turn, and reads the full body only on judged relevance ("Discovery" stage).
- [Source: https://antigravity.google/docs/agent/] The core Agent is described as composed of four elements — reasoning model, Tools, Artifacts, Knowledge — but the fetched page did not spell out a discovery protocol for enumerating available tools/MCP servers/commands at runtime.
- [Source: https://antigravity.google/docs/sdk/overview/] In the SDK, capability discovery is implicitly configuration-time: built-in tools, custom Python function registration, Skill loading, and MCP server connections are all wired into an `Agent`/`LocalAgentConfig` object before a session starts, rather than discovered dynamically mid-session.
- [Source: https://antigravity.google/docs/mcp/] MCP tool namespaces are addressable in the permission system via `mcp(server/tool)`, implying the harness enumerates each connected MCP server's tool list, but the enumeration mechanism itself is not documented.

Not documented / could not verify: any equivalent of a runtime "list available tools" introspection call/command for end users, beyond the `/mcp` and `/skills` CLI panels which are UI surfaces rather than documented protocol/API.

## 14. Agent-Specific Limitations (explicitly documented)

[Source: https://antigravity.google/docs/faq/] Age gate: "unavailable to under-18 users," requiring Google age verification. Availability: 224+ countries/territories, with explicit regional exclusions; Google One AI paid plans unavailable in 33 regions. Personal Gmail accounts are recommended; Google Workspace accounts "may experience authentication challenges." Explicit ToS restriction: "Antigravity logins cannot be used with external software like Claude Code or OpenClaw — doing so violates Terms of Service and risks account suspension." Running an agent blocks OS sleep mode. Data collection is opt-out via Settings, but retention specifics are not detailed in the FAQ.

[Source: https://antigravity.google/docs/subagents/] Hard nesting limit of 10 subagent levels; a misspelled/unmapped tool name passed to a subagent can hang the subagent process (documented as a known gotcha, not just a theoretical risk).

[Source: https://antigravity.google/docs/mcp/ troubleshooting content] One malformed MCP server config entry can block *all* configured MCP servers from loading (fails closed for the whole set, not just the bad entry).

[Source: https://antigravity.google/docs/permissions/] Scope-widening on Ask-prompts is supported for file/URL/MCP permissions but explicitly not for terminal commands — terminal approvals cannot be broadened inline the same way.

[Source: search-quoted, ai.google.dev] On the separate Gemini-API-hosted "Antigravity agent" variant: `file_search`, `computer_use`, and `google_maps` tools are "not yet supported," and structured outputs are not supported. This is a limitation of the **API-hosted variant**, not necessarily the desktop/IDE/CLI product, and should not be assumed to transfer.

Not documented / could not verify: rate limits, maximum context/window enforcement behavior in practice, exact data-retention windows for Knowledge Items or Artifacts, and offline/air-gapped operation support.

---

## Preliminary cross-ecosystem notes (to be reconciled in the comparison doc)

*(All of the below are preliminary, first-pass impressions from a single ecosystem's docs — not conclusions. To be reconciled once other ecosystems are researched.)*

**1. Capabilities that look likely to be universal across coding agents:**
- A markdown-based "skill/procedure" packaging format with frontmatter metadata + progressive/on-demand loading (name+description first, full body only when relevant) — this pattern (explicitly framed by Antigravity's own docs as adopting "the open industry standard for Agent Skills" / "the cross-platform agent specification") strongly suggests a shared, cross-vendor SKILL.md convention already exists or is emerging, not an Antigravity invention.
- A "rules"/standing-instructions file, split into global (user-level, all projects) vs. project/workspace-level, with the project file living in a dotted config directory at the repo root.
- MCP-as-client support with a JSON config keyed by `mcpServers`, `command`/`args`/`env` for local stdio servers, and a remote URL + auth-header variant for hosted servers — this maps directly onto the now-common MCP client config shape used elsewhere.
- An allow/ask/deny (or equivalent) permission model gating file writes, shell commands, and network/tool access, with sensible defaults (workspace files more trusted than outside-workspace, commands/network less trusted by default).
- Hooks around a tool-use lifecycle (pre/post tool call) for validation, linting, and observability.

**2. Capabilities that look distinctly Antigravity/vendor-specific:**
- **Knowledge Items** as an automatically-generated, agent-curated persistent memory distilled by a dedicated "Knowledge Subagent" at the end of every conversation — this is a specific architectural choice (separate subagent + curated facts + per-item metadata.json/artifacts folder) that goes further than a simple memory file.
- **Artifacts** as a first-class, UI-rendered deliverable type (implementation plans, walkthroughs with screenshots, browser recordings) generated during a distinct "Planning Mode," with inline Google-Doc-style commenting — this is a fairly specific UX/product design choice tied to the "Agent Manager" surface.
- The specific `invoke_subagent` tool contract, the three named built-in subagent types (`research`/`browser`/`self`), the hard 10-level nesting cap, and the "does not inherit conversation history but does inherit safety config" split are all quite specific implementation choices.
- Sidecars (persistent background processes with cron-style scheduling and crash-restart policies, addressable via an `agentapi` CLI) — this is a distinctive automation/scheduling primitive not obviously present elsewhere.
- The Terminal Sandbox implementation detail (macOS Seatbelt / Linux nsjail, with permission grants compiling directly into the sandbox's network allowlist) is Antigravity/Gemini-harness-specific, though the general "sandboxed command execution" concept is likely more universal.

**3. What from Antigravity's model seems like it should inform a vendor-neutral "core" skill schema:**
- The **SKILL.md-with-frontmatter + progressive disclosure** pattern (metadata always visible, body loaded on demand) is a strong candidate for the core schema, especially since Antigravity's own docs frame it as already a cross-vendor standard rather than proprietary.
- The **directory-bundle** shape (SKILL.md + scripts/ + examples/ + resources/) as opposed to a single flat file is worth adopting in the core schema, since Antigravity explicitly migrated away from single-file "Workflows" toward this for stated technical reasons (asset bundling, progressive loading).
- Separating **global vs. project-scoped** storage locations for both skills and rules (with a clear precedence/merge story) is a pattern worth generalizing.
- The **name + third-person description-for-relevance-matching** frontmatter convention (explicitly meant to help an agent decide relevance from metadata alone) is a reusable design detail for how a core schema should instruct authors to write descriptions.

**4. What would require an Antigravity-specific "adapter" (not part of the core schema):**
- Mapping a vendor-neutral skill/tool/permission model onto Antigravity's exact file paths (`~/.gemini/...`, `.agents/...`), its `action(target)` permission-string syntax, and its specific JSON shapes for `hooks.json`, `mcp_config.json`, and `sidecar.json`.
- Any adapter that wants to expose Knowledge Items, Artifacts, or Sidecars specifically — these are Antigravity product surfaces with no confirmed equivalent elsewhere yet, so they'd need to be optional/adapter-only extensions, not assumed core primitives.
- The `invoke_subagent` tool call contract and the three named built-in subagent roles are Antigravity's specific delegation API and would need translation for any other agent's own subagent/task-tool mechanism.

**5. What about Antigravity's behavior should NOT be assumed to hold for other agents:**
- That skills can "define specialized system prompts, tool requirements, and delegate sub-tasks to custom subagents" directly from within a SKILL.md — this couples the skill format to a specific subagent-delegation feature that other ecosystems may not have at all.
- That subagents never inherit conversation history but always inherit safety/sandboxing config — this is one specific design decision among several plausible ones (e.g., other ecosystems might share full history, or might not share safety scoping at all).
- That memory (Knowledge Items) is generated automatically and silently by a background subagent at the end of every conversation with no explicit user action — other ecosystems may require explicit "remember this" actions, or may have no persistent memory feature at all (as apparently is/was the case for third-party reports about Antigravity's own CLI surface, per the unofficial Mem0 blog referenced in section 6 — a reminder that even within one vendor, surfaces can differ).
- The exact allow/ask/deny default split (workspace files = Allow by default, everything else = Ask by default) is a specific default posture, not a guaranteed universal default elsewhere.
- The claim (from unofficial third-party sources only, not confirmed in official docs) that Antigravity "inherits VS Code's workspace-local indexing architecture" and cannot aggregate context across repositories should not be treated as a documented fact about Antigravity, let alone generalized to other agents.
