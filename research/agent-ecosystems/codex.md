# OpenAI Codex — Ecosystem Research

Research date: 2026-09-09. Codex ships across several surfaces that share config but differ in capability:

- **Codex CLI** — local terminal agent (`codex` binary), also embeddable via `codex app`, an IDE extension (VS Code/Cursor/Windsurf), and an "app-server" mode.
- **Codex cloud / Codex web** — hosted agent at chatgpt.com/codex that runs tasks in OpenAI-managed cloud containers, triggerable from GitHub/GitLab/Linear/Slack.
- **ChatGPT desktop app "Work"/"Codex" surfaces** — a GUI wrapper that hosts local Codex sessions and/or delegates to cloud.

Docs live at `developers.openai.com/codex/*`, which as of this research date 308-redirect to `learn.chatgpt.com/docs/*` (same content, new host — OpenAI appears to be consolidating docs under "ChatGPT Learn"). Both URLs are cited below since the redirect may not be permanent; the `developers.openai.com` path is the one referenced by name in search results and the GitHub repo, so treat it as canonical even though it currently forwards.

Primary sources consulted: `developers.openai.com/codex/*` (→ `learn.chatgpt.com/docs/*`), `github.com/openai/codex`, `github.com/openai/skills`, `help.openai.com` Codex articles, `openai.com/index/running-codex-safely` and `openai.com/index/introducing-codex`.

---

## 1. Skills

[Source: https://learn.chatgpt.com/docs/build-skills (redirected from https://developers.openai.com/codex/skills)] Codex has a first-class **Skills** mechanism. A skill is a directory-based package centered on a required `SKILL.md` file, with optional subfolders:

```
my-skill/
├── SKILL.md (required — YAML frontmatter with name + description, then instructions)
├── scripts/ (optional)
├── references/ (optional)
├── assets/ (optional)
└── agents/openai.yaml (optional — invocation policy, tool deps, allow_implicit_invocation)
```

[Source: same] Codex scans skills hierarchically across multiple scopes: repo `.agents/skills` (from CWD up through parent directories to the repo root), user `$HOME/.agents/skills`, admin `/etc/codex/skills`, and system (bundled with Codex).

[Source: same] Invocation is either **explicit** (`$skill-name` in Codex CLI, `@skill-name` in ChatGPT, or a sidebar picker) or **implicit** (Codex auto-selects a skill matching the task description; the `description` field in frontmatter is the trigger signal). Context is managed via "progressive disclosure": the initial skill listing is capped at ≤2% of context or 8,000 characters, with the full `SKILL.md` loaded only once a skill is actually selected.

[Source: same] Skills explicitly "build on the open agent skills standard" hosted at agentskills.io — i.e., Codex did not invent its own competing skill format; it adopted (or claims to adopt) a vendor-neutral standard.

[Source: https://developers.openai.com/codex/config-reference] There is a `skill_approval` control inside the granular `approval_policy` config, meaning skill invocation can require user approval like any other action.

[Source: https://github.com/openai/skills] OpenAI maintains a public catalogue repo (`openai/skills`) organized into `.system` (auto-installed with Codex updates), `.curated` (~38 reviewed, production-ready skills), and `.experimental` tiers, installed via a `$skill-installer` tool (e.g. `$skill-installer gh-address-comments`). **Note**: this repo's own page states it is now deprecated in favor of an "OpenAI Plugins" repository — i.e., OpenAI appears to be folding "skills" distribution into a broader "plugins" concept. This shift was visible only secondhand (via WebFetch of the repo) and could not be independently cross-checked against a second official source in this pass — flagged as an area to re-verify.

[Source: https://learn.chatgpt.com/docs/build-skills] For distribution beyond a single machine/repo, OpenAI recommends bundling skills as **plugins**, which can also carry connectors and MCP servers.

## 2. Rules / project instructions / user instructions (AGENTS.md)

[Source: https://learn.chatgpt.com/docs/agent-configuration/agents-md (redirected from https://developers.openai.com/codex/guides/agents-md)] Codex reads `AGENTS.md` files before doing work, using a three-tier precedence system:

1. **Global scope** — Codex home directory (default `~/.codex`): checks `AGENTS.override.md` first, then `AGENTS.md`; uses only the first non-empty file found.
2. **Project scope** — walks from the Git root down to the current working directory, checking each directory level for `AGENTS.override.md`, then `AGENTS.md`, then any configured fallback filenames; includes at most one file per directory.
3. **Merge order** — files are concatenated root-first, downward; files closer to the working directory appear later in the combined prompt and therefore effectively override earlier/broader guidance.

[Source: same] Size is capped by `project_doc_max_bytes` (32 KiB default); once the cumulative byte limit is hit, no further files are appended. Empty files are skipped.

[Source: https://learn.chatgpt.com/docs/config-file/config-advanced (redirected from https://developers.openai.com/codex/config-advanced)] Fallback filenames are configurable: `project_doc_fallback_filenames = ["TEAM_GUIDE.md", ".agents.md"]` lets teams use non-standard filenames if `AGENTS.md` is absent. `CODEX_HOME` can be redirected per user profile.

There is no separate "user preference" instructions file distinct from `AGENTS.md` at global scope — the global `~/.codex/AGENTS.md` (or override) serves that role.

## 3. Context and context loading

[Source: https://learn.chatgpt.com/docs (redirected from https://developers.openai.com/codex) and https://learn.chatgpt.com/docs/build-skills] Confirmed automatic context sources: `AGENTS.md` chain (see §2), and skill listings (name+description only, until a skill is selected — "progressive disclosure").

[Inference, not confirmed in docs] The CLI's terminal status bar shows git branch/model/token usage (per a GitHub issue thread found in search, not an official doc), suggesting Codex is git-aware at the UI level, but no official doc was found describing an automatic full-repo scan/index step at session start comparable to, e.g., automatic directory tree loading. **Not documented / could not verify**: whether Codex proactively loads a repo file tree, README, or package manifests into context at session start beyond what the model chooses to read via tools.

[Source: https://learn.chatgpt.com/docs/customization/memories?surface=app] Separately, the **memories** feature (see §6) injects previously-extracted, cross-session notes into new sessions when enabled — this is the one confirmed "automatic context beyond the current repo" mechanism.

Overall: **Not documented / could not verify** — a single canonical "what Codex loads automatically at session start" reference page. Context loading appears to be primarily: (a) AGENTS.md chain, always: (b) skill index, always; (c) memories, opt-in; (d) everything else via explicit tool calls (reading files, running `git status`/`ls`, etc.) that the model issues itself rather than a fixed pre-load step.

## 4. Tools and tool calling

[Source: https://learn.chatgpt.com/docs (via developers.openai.com/codex)] Documented built-in tools/capabilities include: **Shell** (execute system commands), **Apply Patch** (structured diff-based file editing), **Computer Use** (interact with GUI applications), **Browser** (web navigation/interaction), **Code Interpreter**, plus web search, image generation, and file handling.

[Source: WebSearch of GitHub apply-patch docs, e.g. https://github.com/openai/codex/blob/main/codex-rs/apply-patch/apply_patch_tool_instructions.md — page returned 404 on direct fetch at research time, so treat as **unverified in this pass**] Community/derivative sources describe an `apply_patch` shell-invoked tool using a custom envelope diff format (`*** Add File:`, etc.) rather than raw unified diffs — this is Codex's distinctive file-edit mechanism, analogous to but not identical to a plain `str_replace`/patch tool. Flagging this as needing re-verification directly against openai/codex source since the doc page 404'd for me.

[Source: https://github.com/openai/codex/issues/26133, a GitHub issue — **community-reported, not official doc**] Some users report that even when Browser/Computer-Use plugins are enabled in config, the tools are not always exposed as callable — suggesting these are still maturing/gated features rather than uniformly available. **Not documented / could not verify** as an official statement of limitation.

[Source: https://learn.chatgpt.com/docs/permissions and https://learn.chatgpt.com/docs/agent-approvals-security] Tool calling is gated by a two-layer model: a **sandbox** (technical boundary: filesystem/network access) and an **approval policy** (when to pause and ask). See §5 for detail. Custom tools are added exclusively via MCP servers (§9) — there is no separate "define an arbitrary custom tool" mechanism outside MCP documented.

## 5. File access and repository understanding

[Source: https://learn.chatgpt.com/docs/permissions] Codex uses **permission profiles** combining filesystem rules and network rules. Three built-in profiles: `:read-only`, `:workspace` (read/write within workspace roots + temp dirs), `:danger-full-access` (no sandbox). Filesystem access has three levels per path: `read`, `write`, `deny`, with `deny` > `write` > `read` at matching specificity.

[Source: https://learn.chatgpt.com/docs/agent-approvals-security] Sandbox enforcement mechanism differs by surface: **Codex Cloud** uses isolated OpenAI-managed containers (setup phase has network access; agent phase defaults offline). **CLI/IDE extension** uses OS-level sandboxing — Seatbelt on macOS, `bwrap`/`seccomp` on Linux, native Windows Sandbox on Windows.

[Source: same] Defaults: network access off; write access limited to the active workspace; `.git/`, `.agents/`, `.codex/` remain **read-only** even when the rest of the workspace is writable (protected paths), per https://learn.chatgpt.com/docs/config-file/config-advanced.

[Source: https://learn.chatgpt.com/docs/config-file/config-reference] `sandbox_mode` = `read-only | workspace-write | danger-full-access`. Network access within `workspace-write` is a separate toggle, `sandbox_workspace_write.network_access` (default `false`).

[Source: https://learn.chatgpt.com/docs/cloud/internet-access] For the cloud agent specifically: internet access during the **agent phase** is off by default; **setup scripts** always have internet access (to install dependencies). Per-environment settings: Off / On / Restricted-On (domain allowlist + HTTP method filtering, e.g., allow only GET/HEAD/OPTIONS to block exfiltration via POST/PUT/PATCH/DELETE). A "common dependencies" preset allowlists ~80 domains (GitHub, GitLab, npm, PyPI, RubyGems, Docker/Quay, Go/Rust/Java repos).

[Source: same] Documented risk callout: enabling internet access exposes prompt-injection risk from untrusted web content (e.g., hidden instructions in a GitHub issue body) that could cause code/secret exfiltration — explicitly named as a known hazard, not hidden.

[Source: https://learn.chatgpt.com/docs/config-file/config-reference] An experimental `[features.network_proxy]` can enforce domain-level allow/deny even for the local CLI sandbox (`*.example.com`, `**.example.com`, `*` patterns), off by default.

File editing itself is done via the `apply_patch` tool (see §4) plus shell commands; there is no separate "repository understanding"/indexing feature documented — understanding is achieved by the model reading files via tool calls, not a pre-built index (**not documented / could not verify** any RAG/embedding-based repo index).

## 6. Memory

[Source: https://learn.chatgpt.com/docs/customization/memories?surface=app] Codex CLI (v0.119.0+ per secondary sources) has a **memories** feature: a per-user context system that learns from prior threads/chats and injects relevant notes into future sessions.

- **Storage**: local, under `~/.codex/memories/` (path follows `CODEX_HOME`). Stores "summaries, durable entries, recent inputs, and supporting evidence from prior chats."
- **Scope**: per-user (scoped to `$CODEX_HOME`), **not per-project**.
- **Opt-in**: disabled by default. Enable via Settings → Personalization in the desktop app, or `memories = true` under `[features]` in `config.toml`.
- **Generation**: automatic background consolidation between sessions (not mid-turn); skips short-lived/active sessions; redacts secrets from generated memory content.
- **Config keys**: `memories.use_memories` (inject existing memories, default true once feature is on), `memories.generate_memories` (store new threads as memory input, default true), `memories.max_rollout_age_days` (default 30, clamped 0–90), `memories.min_rollout_idle_hours`, `memories.consolidation_model` / `extract_model` (model overrides), `memories.disable_on_external_context`, `memories.min_rate_limit_remaining_percent`.
- **Per-session control**: `/memories` slash command lets a single chat opt in/out of using or generating memories.
- **Availability**: works in Codex CLI, IDE extension, and the ChatGPT desktop app's local Codex sessions — but **ChatGPT web/cloud interfaces maintain a separate memory system** and this local memory store is explicitly not shared with it. [Source: same]

There is no cross-project shared memory, and no documented long-term "skill learned from experience" mechanism beyond this — memories are free-text notes injected as context, not a structured skill-acquisition system.

## 7. Sub-agents and delegation

[Source: https://learn.chatgpt.com/docs/agent-configuration/subagents (redirected from https://developers.openai.com/codex/subagents)] Codex supports **subagents**: the primary agent can spawn specialized agents to run in parallel on independent sub-tasks and consolidate results, explicitly framed as a fix for "context pollution"/"context rot" on the main thread.

- **Availability**: ChatGPT Work (hosted), local Codex (CLI/IDE extension/desktop app). At most intelligence levels, delegation must be explicitly requested by the user or triggered by AGENTS.md/skill instructions; only at the highest tier ("Ultra") can Codex delegate proactively without being asked.
- **Built-in agent types**: `default` (general fallback), `worker` (execution-focused), `explorer` (read-heavy exploration).
- **Custom agents**: standalone TOML files under `~/.codex/agents/` (personal) or `.codex/agents/` (project-scoped). Required fields: `name`, `description`, `developer_instructions`. Optional: `model`, `model_reasoning_effort`, `sandbox_mode`, `mcp_servers`, `skills.config` (per-agent skill enable/disable).
- **Global config** under `[agents]` in `config.toml`: `agents.enabled`, `agents.max_concurrent_threads_per_session`, `agents.default_subagent_model`, `agents.default_subagent_reasoning_effort`, `agents.interrupt_message`.
- **Sandbox/approval inheritance**: subagents inherit the parent's sandbox policy and approval mode by default; custom agent definitions can override this per-agent (e.g., force read-only).
- **UI**: `/agent` (and `/subagents`) slash commands inspect/switch between running agent threads.
- **Documented limitation**: "Subagent workflows consume more tokens than comparable single-agent runs" and they are "better for read-heavy tasks (exploration, tests, triage) than write-heavy parallel editing," since parallel edits risk conflicts/coordination overhead. ChatGPT Work does not expose local sandbox/approval-mode controls for subagents (those are CLI/local-only knobs).

[Source: WebSearch result referencing developers.openai.com/codex/guides/agents-sdk] Separately, Codex CLI can be exposed as an MCP server and orchestrated externally via the **OpenAI Agents SDK**, enabling a distinct, more deterministic multi-agent pipeline outside of the built-in subagent feature — this is a different mechanism (external orchestration vs in-product delegation) and was not deeply explored in this pass; flagged for follow-up if the comparison doc needs it.

## 8. Hooks

[Source: https://learn.chatgpt.com/docs/hooks (redirected from https://developers.openai.com/codex/hooks)] Codex has a lifecycle hooks system.

- **Events**: `PreToolUse`, `PermissionRequest`, `PostToolUse`, `PreCompact`, `PostCompact`, `UserPromptSubmit`, `SubagentStart`, `SubagentStop`, `Stop`, `Interrupt`, `SessionStart`, `SessionEnd`.
- **Config location**: `hooks.json` in `CODEX_HOME`, or an inline `[hooks]` table in `config.toml`.
- **Structure**: event → matcher group(s) (regex filter on tool name, e.g. `Bash`, `mcp__filesystem__read_file`, or trigger source like `startup|resume|clear|compact`) → handler(s). Omitting `matcher` or using `"*"` matches everything; `UserPromptSubmit`, `Stop`, `Interrupt` ignore matcher values entirely.
- **Handler types**: `type: "command"` (shell script, JSON on stdin/stdout) or `type: "mcp_tool"` (calls a tool on a connected MCP server).
- **Blocking semantics**: `PreToolUse` can deny or rewrite a tool call before it runs (`{"decision": "block", "reason": "…"}`) — the only event that can outright block an action pre-execution besides `PermissionRequest` (approve/deny an approval prompt; multiple hook decisions resolve to "most restrictive" i.e. deny wins). `PostToolUse` cannot undo a completed action but can replace/append feedback to the result.
- **Async**: `"async": true` runs a hook backgrounded (non-blocking); up to 8 concurrent background hooks per session; async hooks cannot block operations, and their output surfaces at the next safe point in the conversation.
- **Availability**: full support across CLI, cloud (subject to cloud-environment constraints), desktop app, and IDE extensions — i.e., not CLI-exclusive.
- **Trust model**: non-managed hooks require explicit user review/trust before they run; admins can force a managed-only mode via `requirements.toml` (`allow_managed_hooks_only = true`) to prevent arbitrary user-authored hooks in managed deployments.

## 9. Commands (custom/slash commands)

[Source: https://learn.chatgpt.com/docs/custom-prompts (redirected from https://developers.openai.com/codex/custom-prompts)] Codex has a **custom prompts** mechanism, but it is explicitly marked **deprecated**: "Use skills for reusable instructions that Codex can invoke explicitly or implicitly."

- Markdown files in `$CODEX_HOME/prompts/` (default `~/.codex/prompts/`); only top-level `.md` files are loaded (no subdirectory/repo sharing).
- Filename (minus `.md`) becomes the command name; invoked as `/prompts:<name>` or, per some phrasing, the bare prompt name.
- YAML frontmatter supports `description` and `argument-hint`.
- Placeholders: `$1`…`$9` (positional), `$ARGUMENTS` (all args), named uppercase placeholders like `$FILE`/`$TICKET_ID` populated via `KEY=value` args, `$$` for a literal `$`.
- Prompts load at session start; edits require a session restart.

[Source: https://learn.chatgpt.com/docs/developer-commands?surface=cli (redirected from https://developers.openai.com/codex/cli/reference)] Separately, Codex has a fixed set of **built-in slash commands** for steering an active session: `/permissions`, `/ide`, `/keymap`, `/vim`, `/agent`, `/subagents`, `/apps`, `/plugins`, `/hooks`, `/memories`, `/clear`. These are product UI commands, not user-definable.

[Source: same] Top-level CLI subcommands (distinct from in-session slash commands): `codex` (launch TUI), `codex exec`/`codex e` (non-interactive scripted run), `codex review`, `codex resume`, `codex fork`, `codex archive`/`unarchive`/`delete`, `codex sandbox`, `codex app`, `codex app-server`, `codex remote-control`, `codex mcp` (manage MCP servers), `codex plugin` / `codex plugin marketplace`, `codex login`/`logout`, `codex doctor`, `codex features`, `codex completion`, `codex update`.

Net effect: the officially-recommended reusable/shareable-command mechanism going forward is **skills**, not custom prompts — custom prompts are legacy and user/local-only (not repo-shareable).

## 10. MCP support

[Source: https://learn.chatgpt.com/docs/extend/mcp?surface=cli (redirected from https://developers.openai.com/codex/mcp)] Codex is an MCP **client**: the ChatGPT desktop app, Codex CLI, and IDE extension all support MCP servers and **share the same MCP configuration** (configure once, works everywhere on that host).

- **Server types**: STDIO (local process via a command) and Streamable HTTP (URL-addressed).
- **Config location/format**: `~/.codex/config.toml` (or project `.codex/config.toml`), one `[mcp_servers.<name>]` table per server.
  - STDIO example: `command = "npx"`, `args = [...]`, `env_vars = [...]`.
  - HTTP example: `url = "https://mcp.figma.com/mcp"`, `bearer_token_env_var = "FIGMA_OAUTH_TOKEN"`.
- **Auth**: bearer tokens (env var or static header), OAuth (including CIMD/DCR client registration), ChatGPT-session auth for trusted first-party servers, custom headers.
- **Per-server config fields** [Source: https://learn.chatgpt.com/docs/config-file/config-reference]: `enabled` (bool, default true), `required` (fail startup if it can't init), `default_tools_approval_mode` (`auto | prompt | writes | approve`), `enabled_tools` (allowlist).
- **CLI management**: `codex mcp add <name>`, `codex mcp list`, `codex mcp get <name>`, `codex mcp remove <name>`, `codex mcp login <name>`, `codex mcp logout <name>`.
- **Codex as MCP server**: yes — `codex mcp-server` (described elsewhere as experimental) exposes Codex itself as an MCP server so other MCP clients/orchestrators (e.g., the OpenAI Agents SDK) can drive it.
- **Elicitations**: the approval-policy granular mode includes `mcp_elicitations` as its own approval category, meaning MCP tool-call elicitation prompts are governed distinctly from generic tool approvals.
- OpenAI also hosts its own public docs MCP server at `https://developers.openai.com/mcp` (read-only search over OpenAI dev docs) as a reference/example server. [Source: WebSearch snippet citing developers.openai.com/learn/docs-mcp]

## 11. Configuration

[Source: https://learn.chatgpt.com/docs/config-file/config-basic and .../config-advanced and .../config-reference (redirected from developers.openai.com/codex/config-basic|advanced|reference)]

**File locations & precedence** (highest to lowest):
1. CLI flags / `--config` overrides
2. Project config (`.codex/config.toml`, closest to CWD wins) — **only loaded for trusted projects**; untrusted projects skip this layer
3. Profile file (`--profile name` → `~/.codex/<name>.config.toml`)
4. User config (`~/.codex/config.toml`)
5. System config (`/etc/codex/config.toml` on Unix, if present)
6. Built-in defaults

**Notable top-level settings** (non-exhaustive, per config-reference):
- `model`, `model_provider`, `model_reasoning_effort` (`minimal|low|medium|high|xhigh`), `model_context_window`
- `sandbox_mode` (`read-only|workspace-write|danger-full-access`) — mutually exclusive with `default_permissions` (named permission profile)
- `approval_policy` (`untrusted|on-request|never`, or granular per-category object: `sandbox_approval`, `rules`, `mcp_elicitations`, `request_permissions`, `skill_approval`)
- `approvals_reviewer` (`user|auto_review`)
- `mcp_servers.*` (§10)
- `features.hooks`, `hooks.*` (§8)
- `features.memories`, `memories.*` (§6)
- `shell_environment_policy.inherit` (`all|core|none`), `.filters`
- `allow_login_shell` (default true)
- `features.network_proxy` + `.domains` (experimental, off by default)
- `web_search` (`disabled|cached|indexed|live`, default `cached`)
- `apps.<id>.enabled`, `apps._default.destructive_enabled`, `apps._default.open_world_enabled`
- `project_doc_max_bytes` (32 KiB default), `project_doc_fallback_filenames`
- `agents.*` (§7)

Config can also be edited via a GUI in the IDE extension (gear icon) rather than hand-editing TOML.

## 12. Reusable instructions (across projects)

[Source: §2 and §9 material] Two documented mechanisms:
1. **Global `AGENTS.md`** (or `AGENTS.override.md`) in `~/.codex` (or wherever `CODEX_HOME` points) — applies to every project on that machine/profile, layered under project-level `AGENTS.md`.
2. **User-scope skills** in `$HOME/.agents/skills` — personal, cross-project skills (as distinct from repo-scoped `.agents/skills` at various directory levels).

For sharing across *people/teams* rather than just across a single user's projects, the documented path is packaging as a **skill** and distributing it via a **plugin**/marketplace (`codex plugin`, `codex plugin marketplace`) or a shared skills catalogue repo (like `openai/skills`), rather than a config-file mechanism.

Custom prompts (§9) are explicitly *not* positioned as a cross-project/reusable-sharing mechanism — they're deprecated, local-only, and non-shareable via repo.

## 13. Capability discovery

[Source: https://learn.chatgpt.com/docs/build-skills] The clearest documented discovery mechanism is for **skills**: Codex builds a lightweight index (name + description only, capped at ≤2% of context / 8,000 characters) of all discoverable skills across scopes so the model can decide whether to invoke one implicitly, without paying the full context cost of every `SKILL.md` up front.

[Source: §10 / config-reference] For **MCP tools**, `enabled_tools` allowlists and `default_tools_approval_mode` govern what's exposed per server, but the actual listing mechanism (how the model learns what tools a connected MCP server offers) follows standard MCP `tools/list` semantics — this is protocol-level, not Codex-specific, and wasn't separately documented by OpenAI beyond pointing at the MCP spec.

[Source: §4, unverified] A `tool_search.tool_search_tool` was referenced in a secondary (non-official) search snippet describing Codex's runtime tool list, implying a meta-tool for discovering other tools at runtime — **not documented / could not verify** against an official OpenAI page in this pass; flagged for re-verification.

For CLI commands themselves, discovery is conventional: `codex --help`, `codex doctor` (diagnostics), and `codex features` (list/toggle feature flags) are the documented introspection commands. **Not documented / could not verify**: any equivalent of a single unified "list everything this agent can currently do" command spanning skills + MCP tools + subagents + hooks in one view (each has its own inspection surface: `/plugins`, `/hooks`, `/agent`, `codex mcp list`, etc.).

## 14. Agent-specific limitations

Explicitly documented constraints (not inferred):

- [Source: https://learn.chatgpt.com/docs/agent-approvals-security] Network access is **off by default** everywhere; write access is confined to the active workspace; `.git/`, `.agents/`, `.codex/` stay read-only even inside an otherwise-writable workspace.
- [Source: https://learn.chatgpt.com/docs/cloud/internet-access] Cloud agent phase has **no internet access by default**; only setup scripts get it; agent-phase internet access must be explicitly turned on per environment and can be restricted to an allowlist + safe HTTP methods (GET/HEAD/OPTIONS) specifically to reduce data-exfiltration risk.
- [Source: same] Explicit documented threat model callout: enabling internet access exposes the agent to **prompt injection from untrusted web/issue content**, which the docs illustrate can lead to credential/code exfiltration — OpenAI documents this as a known risk of a supported feature, not a hypothetical.
- [Source: https://learn.chatgpt.com/docs/agent-approvals-security] "Cannot be proxied through command sandbox": web search, app/connector tools, MCP servers, browser activity, and model/auth requests fall outside the local command-sandbox boundary — meaning the filesystem/network sandbox around shell commands does **not** uniformly cover every capability Codex has; those other surfaces have their own separate access controls.
- [Source: https://learn.chatgpt.com/docs/agent-configuration/subagents] Subagents are documented as weaker for write-heavy/parallel-editing tasks (conflict risk) and strictly more token-expensive than single-agent execution; ChatGPT Work's subagents don't expose local sandbox/approval controls at all.
- [Source: https://learn.chatgpt.com/docs/customization/memories?surface=app] Local-Codex memories and ChatGPT-web/cloud memories are **separate, non-interoperating stores** — a documented fragmentation, not a bug.
- [Source: https://learn.chatgpt.com/docs/custom-prompts] Custom prompts are deprecated and explicitly limited to top-level markdown files in one local directory — not shareable via a repo, unlike skills.
- [Source: https://learn.chatgpt.com/docs/config-file/config-advanced] Project-level config/AGENTS.md/skills only load for **trusted** projects; untrusted projects silently skip those layers (fall back to user/system config only) — a security boundary worth noting for any adapter that assumes project config always applies.
- [Community-reported, unverified officially] A GitHub issue (https://github.com/openai/codex/issues/26133) reports Browser/Computer-Use tools sometimes configured but not actually exposed as callable — treat built-in Browser/Computer-Use support as still maturing rather than uniformly guaranteed.

---

## Preliminary cross-ecosystem notes (to be reconciled in the comparison doc)

*(All bullets here are explicitly preliminary/best-effort, per the task instructions — not conclusions to design against yet.)*

**1. Likely-universal capabilities (other agents probably have an equivalent):**
- A project-level "rules/instructions" file discovered by walking up the directory tree (Codex: `AGENTS.md`) — this pattern (and the literal filename `AGENTS.md`) is explicitly cross-vendor already; Codex's contribution is mainly the override-file convention (`AGENTS.override.md`) and configurable fallback filenames.
- MCP client support with a `command`/`args`/`env` (stdio) vs `url` (HTTP) split — this mirrors the MCP spec itself, so any MCP-client agent should look nearly identical here.
- Some notion of approval/permission gating for shell commands and file writes.
- A packaged, reusable "skill" folder with metadata + instructions + optional scripts, loaded lazily/progressively — Codex explicitly frames this as adopting an external "open agent skills standard" (agentskills.io) rather than inventing its own, which suggests the *format* itself may already be closer to vendor-neutral than the rest of Codex's feature set.

**2. Distinctly Codex-specific / vendor-specific:**
- The specific TOML config schema and its precedence chain (CLI flag > project > profile > user > system), including the `:read-only`/`:workspace`/`:danger-full-access` named permission-profile system.
- `apply_patch`'s custom envelope diff format (if confirmed) as the file-edit primitive, rather than a plain unified diff or line-replace tool.
- The **memories** feature's specific mechanics (background consolidation, `max_rollout_age_days`, redaction-on-generation) — the general idea of cross-session memory is not unique, but this exact implementation is.
- The three-tier built-in subagent roster (`default`/`worker`/`explorer`) and the "Ultra intelligence level can delegate proactively" gating — tying delegation autonomy to a model/tier rather than a user-set policy flag is a distinctly OpenAI-shaped design.
- The hooks event taxonomy (`PreCompact`/`PostCompact`, `PermissionRequest`, `SubagentStart`/`SubagentStop`) — plausible other agents have hooks, but this exact event set/naming is Codex's.
- The deprecation of "custom prompts" in favor of skills as the sole forward-looking reusable-instruction mechanism — signals OpenAI is deliberately collapsing what other ecosystems might keep as two separate features (slash-command snippets vs. skills) into one.

**3. What seems like it should inform a vendor-neutral "core" skill schema:**
- Directory-based package with one required entry-point file carrying `name` + `description` frontmatter, optional `scripts/`, `references/`, `assets/` subfolders — this shape recurs enough (and Codex explicitly cites an external standard for it) that it's a reasonable default shape for a core schema.
- A lazy/progressive-disclosure discovery model: cheap metadata index first, full instructions only on selection — worth carrying into a core schema as a *recommended loading strategy* rather than assuming agents always load full skill bodies.
- Explicit scoping tiers (repo → user → admin/system) as a discovery search path, with closer-scope files winning — mirrors the AGENTS.md precedence pattern and could be a shared "scope resolution" primitive in core, not just a skill-specific one.
- A separate "approval required for this skill" flag as first-class metadata (Codex's `skill_approval` / `allow_implicit_invocation`) — a core schema probably wants an approval/trust field independent of any one vendor's approval-policy implementation.

**4. What would need a Codex-specific adapter to translate a generic skill into something Codex can consume:**
- Mapping a generic skill's tool dependencies onto Codex's MCP-server-only extension model (Codex has no "arbitrary custom tool" concept outside MCP + the fixed built-in tool set) — a generic skill that assumes some other tool-registration mechanism would need its tools re-expressed as an MCP server or dropped.
- Translating any generic "always trust this skill" vs "ask every time" flag into Codex's specific `approval_policy.granular.skill_approval` / `agents/openai.yaml` `allow_implicit_invocation` fields.
- Placing the skill at the exact expected path per scope (`.agents/skills` at repo/user/admin levels) and producing a `SKILL.md` with Codex's expected frontmatter shape, plus an optional `agents/openai.yaml` if the skill needs UI/invocation-policy hints Codex-side.
- If the generic skill wants to declare a preferred model/reasoning-effort for its own execution, that would map to Codex's *subagent* config (`~/.codex/agents/*.toml`) rather than the skill file itself — i.e., "run this skill as a dedicated subagent" is a two-object translation (skill + agent definition), not one.

**5. What should NOT be assumed to hold for other agents:**
- That "skills" and "custom commands"/"slash commands" are the same feature — Codex explicitly split these historically (custom prompts vs. skills) and is now deprecating one in favor of the other; other agents may keep them permanently distinct, or never have had the deprecated form at all.
- That memory is per-user and local by default, or that it exists at all — Codex's memory is opt-in, local-store, and explicitly *not* unified with its own cloud/web product's memory; assuming any particular default (on/off, scope, storage location) for another agent would be unfounded.
- That subagent delegation requires an explicit user ask except at a specific "top tier" — this ties autonomy to a commercial tier/intelligence level, which is an OpenAI-specific product decision, not a general behavior of "agents with subagent support."
- That network access is sandboxed uniformly across all agent capabilities — Codex explicitly documents that its shell-command sandbox does *not* cover web search, connectors, MCP servers, or browser tools, each of which has independent access controls. Another agent's "sandbox" claim should not be assumed to have the same gaps (or the same coverage).
- That project-level config/instructions always apply — Codex's "trusted projects only" gate for project config/AGENTS.md/skills is a specific trust model; other agents may apply project config unconditionally, or gate trust differently.
