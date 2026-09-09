# Agent Capability Map

**Scope.** This map inventories the execution-relevant *capabilities* of the seven researched AI coding-agent ecosystems (Claude Code, Codex, Cursor, Antigravity, Windsurf/Devin, VS Code, and MCP itself as a protocol layer) — the things a future skill in this project might need the underlying agent to actually be able to do (run shell commands, drive a browser, connect to a database over MCP, remember things across sessions, and so on). For each capability it shows which ecosystems support it, which explicitly limit or lack it, and which of the 44 researched technologies depend on or relate to it. It closes with a synthesis of what this means for designing technology-focused skills that need to work across more than one agent.

**Sourcing rule.** Every fact below comes from the compiled JSON data supplied for this task (`agentCapabilities` and `technologyIndex`) — nothing here was invented, and no new research was performed. Where the underlying research is thin, silent, or conflicting on a point, that is stated explicitly rather than papered over. Passages introduced by **[Synthesis: ...]** are new cross-cutting inferences this map draws by combining two or more individually-stated facts from the data; they are not claims the underlying research made directly.

**What this is not.** This document maps agent capabilities for reference. It does not define, design, or write any "skill" (no SKILL.md content, no step-by-step agent instructions) — it exists to inform later skill design.

---

## Contents

1. [How to read an entry](#how-to-read-an-entry)
2. [Capability index](#capability-index)
3. [Shell/command execution with a sandboxing model](#1-shellcommand-execution-with-a-sandboxing-model)
4. [Docker/container-based execution](#2-dockercontainer-based-execution)
5. [Browser automation / GUI interaction](#3-browser-automation--gui-interaction)
6. [MCP client support](#4-mcp-client-support-stdio--remote-transports-including-databasecache-servers)
7. [Persistent filesystem/repo write access](#5-persistent-filesystemrepo-write-access)
8. [Network/internet access defaults](#6-networkinternet-access-defaults)
9. [Lifecycle hooks / enforced automation](#7-lifecycle-hooks--enforced-automation)
10. [Sub-agent delegation](#8-sub-agent-delegation-isolated-context-workers)
11. [Semantic/RAG-based repository search](#9-semanticrag-based-repository-search-standing-index)
12. [Persistent memory across sessions](#10-persistent-memory-across-sessions)
13. [Permission/approval model for risky operations](#11-permissionapproval-model-for-risky-operations)
14. [Reciprocal MCP server capability](#12-reciprocal-mcp-server-capability-agent-exposing-itself-as-an-mcp-server)
15. [Git/GitHub integration and PR automation](#13-gitgithub-integration-and-pr-automation)
16. [What this means for skill design](#what-this-means-for-skill-design)
17. [Coverage gaps in the underlying research](#coverage-gaps-in-the-underlying-research)

---

## How to read an entry

Each capability gets:

- **What it is** — the description carried from the compiled data.
- **Supported by** — ecosystems that document the capability, with the specific note and citation preserved verbatim.
- **Not supported / limited by** — ecosystems (or the ecosystem landscape as a whole) documented as lacking, restricting, or self-disclosing weaknesses in the capability.
- **Depends on this (from the 44 technologies)** — the technologies the data links to this capability, with a one-line "why" drawn from `technologyIndex.coreConcepts` where that adds clarity. This list is copied from the data's `relevantTechnologies` field per capability — it reflects what the underlying research judged relevant, not an exhaustive dependency audit.

A capability with a short "not supported" list is not necessarily universally solid — see each entry's cross-vendor caveats before assuming a hard guarantee.

---

## Capability index

| # | Capability | Broadest support | Notable gaps |
|---|---|---|---|
| 1 | Shell/command execution with a sandboxing model | All 7 ecosystems | Enforcement universally self-described as imperfect; Codex's sandbox excludes web/connectors/MCP/browser |
| 2 | Docker/container-based execution | Codex, VS Code, Antigravity (partial) | No ecosystem documents a first-class `docker` orchestration primitive distinct from shell |
| 3 | Browser automation / GUI interaction | Codex, Cursor, Antigravity | Claude Code (none built-in), Windsurf/Devin (none found), Codex (community-reported gaps) |
| 4 | MCP client support | All 7 ecosystems (incl. VS Code) | Codex uses TOML not JSON; Windsurf caps at 100 tools; VS Code sandboxing absent on Windows |
| 5 | Persistent filesystem/repo write access | All 7 ecosystems | Codex protects `.git/`/`.agents/`/`.codex/`; Windsurf blocks `.gitignore`-matched files entirely |
| 6 | Network/internet access defaults | Codex (most granular), Cursor, Antigravity, Windsurf, Claude Code | Codex: sandbox boundary excludes web search/connectors/MCP/browser tools |
| 7 | Lifecycle hooks / enforced automation | All 7 ecosystems except MCP itself | Cursor fail-open by default; VS Code doesn't enforce `matcher`; Windsurf hooks don't run in Restricted Mode |
| 8 | Sub-agent delegation | All 7 ecosystems | History-inheritance and nesting depth vary widely and are unresolved cross-vendor forks |
| 9 | Semantic/RAG-based repository search | Cursor, Windsurf/Devin, VS Code | Claude Code, Codex, Antigravity, MCP itself: no standing index documented |
| 10 | Persistent memory across sessions | Claude Code, Codex, Windsurf/Cascade (legacy), Antigravity, VS Code (preview) | Windsurf/Devin Local actively removed it; Cursor's status unconfirmed; MCP has none by design |
| 11 | Permission/approval model for risky operations | All 7 ecosystems | Universally self-described as best-effort; VS Code's auto-approve is all-or-nothing |
| 12 | Reciprocal MCP server capability | Claude Code, Codex (experimental) | Cursor, Windsurf/Devin, Antigravity, VS Code: none documented |
| 13 | Git/GitHub integration and PR automation | Cursor (Background Agents), Codex (cloud), Claude Code (worktrees) | No ecosystem documents a first-class GitHub Actions integration |

---

## 1. Shell/command execution with a sandboxing model

**What it is.** The agent can run arbitrary terminal/shell commands as part of completing a task, gated by some technical sandbox boundary (filesystem/network scoping) distinct from the approval-prompt layer sitting on top of it.

**Supported by:**
- **Claude Code** — Built-in Bash/PowerShell tools (2-min default timeout, 5GB output cap, no persisted env vars); permission rules gate use, but enforcement is client-side, not an OS sandbox by default. *(claude-code.md §4, §14; code.claude.com/docs/en/tools-reference, /permissions)*
- **Codex** — Shell tool gated by a two-layer model: permission profile (`:read-only`/`:workspace`/`:danger-full-access`) plus OS-native sandbox — Seatbelt (macOS), bwrap/seccomp (Linux), Windows Sandbox — for CLI/IDE; isolated managed containers for Codex Cloud. *(codex.md §4-5; learn.chatgpt.com/docs/permissions, /agent-approvals-security)*
- **Cursor** — Built-in "run shell commands" tool with configurable terminal profiles; sandboxed "where possible" under Auto-review Run Mode (network/filesystem restricted), explicitly called "best-effort guardrails... not a hard security boundary." *(cursor.md §4; cursor.com/docs/agent/tools, /agent/security)*
- **Antigravity** — Terminal execution gated by the unified permission engine's `command()` action type; Terminal Sandbox provides OS-native kernel isolation — macOS Seatbelt, Linux nsjail (Windows unsupported). *(antigravity.md §4; antigravity.google/docs/permissions/)*
- **Windsurf/Devin** — Cascade's integrated terminal has 4 auto-execution tiers (Disabled/Allowlist/Auto/Turbo); Devin Local replaces this with Deny/Ask/Allow rules plus OS-level filesystem and network-filtering sandboxing. *(windsurf.md; docs.devin.ai/desktop/terminal, /devin-local)*
- **VS Code** — Shell execution is delegated to whichever harness is active (Claude/Codex bring their own shell tool); terminal command allow/deny regex lists exist in settings.json. *(vscode.md §4, §11)*

**Not supported / limited by:**
- **Cross-vendor** — Every vendor that documents this self-discloses the enforcement is imperfect — Cursor calls it "not a security guarantee"; Claude Code documents Bash argument-restriction as bypassable and recommends hooks instead. *(comparison.md Tools and tool calling section)*
- **Codex** — The command sandbox's network/filesystem boundary explicitly does not cover web search, connectors, MCP servers, or browser tools — each has independent, uncoordinated access controls. *(codex.md §14; learn.chatgpt.com/docs/agent-approvals-security)*

**Depends on this (from the 44 technologies):** Docker, Go, Python, GitHub Actions (CI/CD), Husky, Playwright, Jest, Vitest, Vite, ECMAScript, TypeScript, Drizzle ORM, Prisma, TypeORM, MySQL, PostgreSQL, MongoDB, Redis, ClickHouse, OpenSearch — i.e. essentially every technology whose skill would involve running a build, test, or CLI-driven database command depends on shell execution existing at all.

---

## 2. Docker/container-based execution

**What it is.** Whether the agent's own sandbox/execution model is container-based, and/or whether official docs describe a first-class capability for driving container tooling, as opposed to generic shell access to a `docker` binary.

**Supported by:**
- **Codex** — Codex Cloud runs tasks inside OpenAI-managed cloud containers; the cloud "common dependencies" network allowlist preset explicitly names Docker/Quay registries. *(codex.md §5; learn.chatgpt.com/docs/cloud/internet-access)*
- **VS Code** — MCP servers can be declared/launched via a Dev Container (devcontainer.json); a "Cloud" agent-harness target runs on remote provider infrastructure. *(vscode.md §0, §10)*
- **Antigravity** — The permission model names a distinct `unsandboxed()` (container-escape) permission type, implying a container concept exists at the policy layer even though the terminal sandbox itself is OS-native, not container-based. *(antigravity.md §4; antigravity.google/docs/permissions/)*

**Not supported / limited by:**
- **Claude Code** — No documented first-class "run inside Docker" primitive; its own docs frame containers/VMs as a user-provided wrapper (recommending `bypassPermissions` mode only "in isolated environments like containers or VMs"), not something the agent orchestrates itself. *(claude-code.md §14; code.claude.com/docs/en/permissions)*
- **Cursor, Windsurf/Devin** — No documented container-orchestration capability found; execution is OS-native sandboxing or application-level allowlisting, not container management. *(cursor.md §4; windsurf.md Terminal section)*
- **Cross-vendor [Synthesis — absence checked across all seven docs]** — No ecosystem doc researched describes the agent invoking `docker build`/`docker run` as a distinct documented capability separate from ordinary shell/Bash tool use — this appears to be plain shell execution wrapping the docker CLI everywhere, not a separate primitive.

**Depends on this (from the 44 technologies):** Docker, PostgreSQL, MySQL, MongoDB, Redis, ClickHouse, OpenSearch, GitHub Actions (CI/CD), Playwright — the database and CI/testing technologies most likely to be run in a local container for a skill's dev-loop.

---

## 3. Browser automation / GUI interaction

**What it is.** The agent can drive a real or headless browser — navigate, click, screenshot, inspect the DOM — as a distinct tool from plain HTTP fetch/markdown retrieval, relevant to running or verifying Playwright-style workflows and visually checking rendered UI.

**Supported by:**
- **Codex** — Documented built-in "Computer Use" (GUI interaction) and "Browser" (web navigation/interaction) tools. *(codex.md §4; learn.chatgpt.com/docs)*
- **Cursor** — Built-in browser control tool (navigate, screenshot, interact, verify visual changes); a dedicated Browser subagent wraps this via MCP tools and filters noisy DOM data. *(cursor.md §4, §7; cursor.com/docs/agent/tools, /docs/subagents)*
- **Antigravity** — Dedicated Browser Subagent, invocable via `/browser`, integrates with Chrome DevTools MCP, can record webm video of its session. *(antigravity.md §7; antigravity.google/docs/features/, /subagents/)*

**Not supported / limited by:**
- **Claude Code** — No built-in browser-automation tool documented; WebFetch only converts HTML to Markdown via a smaller model (lossy, non-interactive) — interactive browser control would need an external MCP server (e.g. a Playwright MCP server). *(claude-code.md §4; code.claude.com/docs/en/tools-reference)*
- **Codex** — A GitHub issue (community-reported, not an official statement) reports Browser/Computer-Use tools sometimes configured but not exposed as callable — treated as still-maturing, not uniformly guaranteed. *(codex.md §4, §14; github.com/openai/codex/issues/26133)*
- **Windsurf/Devin** — No dedicated built-in browser-automation tool found in the fetched official docs beyond general web search. *(windsurf.md Tools section — absence noted)*

**Depends on this (from the 44 technologies):** Playwright (its own core purpose is browser automation), WebRTC, Google SEO, Google AdSense, React, Vue, Angular, Next.js, Nuxt, Three.js, shadcn/ui, MUI (Material UI), Tailwind CSS, HTML, CSS, Sass — essentially all UI-rendering and frontend-framework technologies where a skill would want to visually verify rendered output.

---

## 4. MCP client support (stdio + remote transports, including database/cache servers)

**What it is.** The agent connects to external Model Context Protocol servers as a client and exposes their tools/resources/prompts alongside built-ins — the mechanism by which a skill could reach a Postgres/Redis/MongoDB MCP server for structured database access without relying on raw shell commands.

**Supported by:**
- **Claude Code** — `.mcp.json` (project) / `~/.claude.json` (user), stdio/http/sse(deprecated)/ws transports; can also itself run as an MCP server via `claude mcp serve`. *(claude-code.md §10; code.claude.com/docs/en/mcp)*
- **Cursor** — `mcp.json`, keyed under `mcpServers`; stdio, SSE, and Streamable HTTP transports; tool calls require approval by default. *(cursor.md §10; cursor.com/docs/mcp)*
- **Codex** — `~/.codex/config.toml` — the only TOML-based MCP config among ecosystems researched; stdio + Streamable HTTP; shared config across CLI/IDE/desktop app. *(codex.md §10; learn.chatgpt.com/docs/extend/mcp)*
- **Windsurf/Devin** — `mcp_config.json`, stdio/Streamable HTTP/SSE; hard cap of 100 total active MCP tools; Devin Local requires explicit approval for MCP tool calls by default. *(windsurf.md MCP support section; docs.devin.ai/desktop/cascade/mcp)*
- **Antigravity** — `mcp_config.json`, stdio + remote HTTP/SSE; an in-app "MCP Store" offers 46+ pre-configured servers including databases. *(antigravity.md §10; antigravity.google/docs/mcp/)*
- **VS Code** — `mcp.json`, http/stdio transports, plus MCP Resources/Prompts/Apps surfaced beyond tools; Dev Container-declared servers supported. *(vscode.md §10; code.visualstudio.com/docs/agent-customization/mcp-servers)*

**Not supported / limited by:**
- **Codex** — Uses TOML instead of the JSON format every other ecosystem researched uses — a real serialization-format incompatibility, not just a path difference. *(comparison.md MCP support section)*
- **Windsurf/Devin** — Caps total simultaneously-active MCP tools at 100 across all connected servers. *(windsurf.md)*
- **VS Code** — MCP server sandboxing (which drives tool-call auto-approval) is not available on Windows at all, and only covers stdio-based servers even where available. *(vscode.md §14)*
- **MCP itself** — The Roots filesystem-hint primitive is deprecated as of the 2026-07-28 spec revision; MCP has no dedicated "repository understanding" primitive beyond whatever a server exposes as ordinary tools/resources. *(mcp.md §5)*

**Depends on this (from the 44 technologies):** PostgreSQL, MySQL, MongoDB, Redis, ClickHouse, OpenSearch, Drizzle ORM, Prisma, TypeORM, Mongoose, GraphQL, OpenAPI, Swagger, GitHub, Docker — this is the single largest `relevantTechnologies` list of any capability, reflecting that MCP is the documented preferred path for structured access to almost every data-layer and API-spec technology in the index.

---

## 5. Persistent filesystem/repo write access

**What it is.** The agent can create, edit, and delete files in the working repository across turns, typically scoped to a bounded "working directory"/workspace concept rather than the whole filesystem.

**Supported by:**
- **Claude Code** — Write/Edit/NotebookEdit tools scoped to "working directories" (launch directory by default, extendable via `--add-dir`); read-only tools don't prompt inside working directories. *(claude-code.md §4-5; code.claude.com/docs/en/permissions)*
- **Codex** — `apply_patch` tool + shell; `sandbox_mode=workspace-write` allows read/write within workspace roots and temp dirs. *(codex.md §4-5; learn.chatgpt.com/docs/config-file/config-reference)*
- **Cursor** — Edit-files tool with suggest+auto-apply edits; workspace trust must be manually enabled. *(cursor.md §4; cursor.com/docs/agent/security)*
- **Windsurf/Devin** — File read/modify respects `.codeiumignore`; Code Mode allows full file creation/edits. *(windsurf.md Tools section)*
- **Antigravity** — `write_file` permission action (implies read); workspace files default to Allow. *(antigravity.md §4; antigravity.google/docs/permissions/)*
- **VS Code** — File edits performed via whichever harness's own edit tool, scoped to the open workspace folder(s). *(vscode.md §4)*

**Not supported / limited by:**
- **Codex** — `.git/`, `.agents/`, `.codex/` remain read-only even when the rest of the workspace is writable — a documented protected-path carve-out. *(codex.md §5, §14)*
- **Windsurf/Devin** — Files matched by `.gitignore` cannot be edited by the agent at all, "not just excluded from indexing/context." *(windsurf.md File access section)*

**Depends on this (from the 44 technologies):** React, Vue, Angular, Next.js, Nuxt, TypeScript, Go, Python, Docker, GitHub Actions (CI/CD), Tailwind CSS, Sass, Husky, Drizzle ORM, Prisma, TypeORM — the frameworks/languages/config technologies whose skills fundamentally require editing source files.

---

## 6. Network/internet access defaults

**What it is.** Whether outbound network calls (package installs, external API calls, doc fetches) are on, restricted to an allowlist, or off by default, and how that default differs between local/interactive sessions and CI-like/cloud execution.

**Supported by:**
- **Codex** — Most granularly documented: network off by default everywhere; cloud agent-phase off by default (setup-phase always on); Restricted-On mode adds a domain allowlist plus HTTP-method filtering (blocks POST/PUT/PATCH/DELETE); a ~80-domain "common dependencies" preset covers npm/PyPI/RubyGems/Docker/Go/Rust/Java registries. *(codex.md §5; learn.chatgpt.com/docs/cloud/internet-access)*
- **Cursor** — Outbound network from agent-run processes restricted by default to GitHub, direct link retrieval, and web search providers — "agents cannot make arbitrary network requests with default settings." *(cursor.md §4; cursor.com/docs/agent/security)*
- **Antigravity** — `read_url`/`execute_url` permission types default to Ask; sandbox mode compiles `read_url` grants directly into the container's outbound network allowlist. *(antigravity.md §4; antigravity.google/docs/permissions/)*
- **Windsurf/Devin** — Devin Local adds network filtering via domain allow/deny lists. *(windsurf.md Permission model section)*
- **Claude Code** — WebFetch denies private/internal addresses by default; settings-reference documents sandbox network isolation as a configurable settings category. *(claude-code.md §4, §11)*

**Not supported / limited by:**
- **Codex** — Explicitly documents that its shell-command sandbox network boundary does not cover web search, connectors, MCP, or browser tools — each has independent access controls, so "network access is off by default" is not a single uniform fact. *(codex.md §14)*
- **Codex** — Enabling internet access is explicitly named as introducing prompt-injection/exfiltration risk from untrusted fetched content — a known, not hidden, hazard. *(codex.md §5)*

**Depends on this (from the 44 technologies):** GitHub, GitHub Actions (CI/CD), React, Vue, Angular, Next.js, Nuxt, TypeScript, ECMAScript, Vite, Jest, Vitest, Playwright, Tailwind CSS, shadcn/ui, MUI (Material UI), OpenAPI, Swagger, GraphQL, Google SEO, Google AdSense — package-install-heavy frontend/testing/build technologies plus anything (Google SEO/AdSense, GraphQL, OpenAPI) whose skill would fetch live external endpoints or docs.

---

## 7. Lifecycle hooks / enforced automation

**What it is.** An external-process hook mechanism (JSON on stdin, exit code as control signal — 2 typically means block) firing at defined points in the agent loop, the closest analog to CI-style enforced gating such as "block this commit unless tests pass."

**Supported by:**
- **Claude Code** — 5 handler types (command/http/mcp_tool/prompt/agent), 30+ named lifecycle events; PreToolUse can block via exit code 2 or structured decision. *(claude-code.md §8; code.claude.com/docs/en/hooks)*
- **Cursor** — 3 hook categories (Agent/Tab/App lifecycle); command-based hooks default fail-open (any non-2 exit code allowed) unless `failClosed:true` is set; prompt-based (LLM-evaluated) hooks also exist. *(cursor.md §8; cursor.com/docs/hooks)*
- **Codex** — `command` and `mcp_tool` handler types; PreToolUse/PermissionRequest can block; multiple hook decisions resolve to "most restrictive wins." *(codex.md §8; learn.chatgpt.com/docs/hooks)*
- **Windsurf/Cascade** — 12 documented hook events; exit code 2 blocks pre-hooks only; post-hooks are logging-only. *(windsurf.md Hooks section; docs.devin.ai/desktop/cascade/hooks)*
- **Antigravity** — 5 lifecycle events (PreToolUse/PostToolUse/PreInvocation/PostInvocation/Stop) via `hooks.json`, JSON stdin/stdout contract. *(antigravity.md §8; antigravity.google/docs/hooks/)*
- **VS Code** — 8 documented lifecycle events, explicitly Preview status; ingests Claude Code's hook config format directly. *(vscode.md §8)*

**Not supported / limited by:**
- **MCP itself** — No hook concept exists at the protocol level. *(mcp.md §8; comparison.md Hooks section)*
- **Cursor** — Fail-open is the documented default (any non-2 exit code = allowed) unless a hook explicitly opts into `failClosed:true` — a live, security-relevant divergence from vendors that may default the other way. *(cursor.md §8; comparison.md Hooks section)*
- **VS Code** — Parses Claude Code's `matcher` field but does not enforce it — "all matching hooks run regardless," a documented fidelity gap even between two vendors both claiming hook support; hooks remain Preview and format may change. *(vscode.md §14)*
- **Windsurf/Cascade** — Hooks don't execute in Restricted Mode; run with full user-account privileges (explicit security warning in docs); unclear whether Devin Local (the newer default agent) supports hooks at all. *(windsurf.md Hooks, Limitations sections)*

**Depends on this (from the 44 technologies):** Husky, GitHub Actions (CI/CD), Jest, Vitest, Playwright — precisely the set of technologies whose entire purpose is enforced gating (git hooks, CI pipelines, test runners).

---

## 8. Sub-agent delegation (isolated context workers)

**What it is.** A parent agent can spawn a subagent with its own context window to run a sub-task — e.g. a test suite or a build — returning a result rather than raw output, typically with a foreground(blocking)/background(async) execution split.

**Supported by:**
- **Claude Code** — Built-in Explore/Plan/general-purpose subagents; `context:fork` inherits the entire parent conversation verbatim; 3-level nesting cap, 20 concurrent. *(claude-code.md §7; code.claude.com/docs/en/sub-agents)*
- **Cursor** — Built-in Explore/Bash/Browser subagents start with fresh context; nesting restricted to "main agent and direct subagents only" (1 level); parallel runs cost ~N× tokens. *(cursor.md §7; cursor.com/docs/subagents)*
- **Codex** — Delegation for context-pollution avoidance; at most tiers must be explicitly requested (only the highest "Ultra" tier can delegate proactively); weaker for write-heavy/parallel-editing tasks. *(codex.md §7; learn.chatgpt.com/docs/agent-configuration/subagents)*
- **Windsurf/Devin Local** — Can spawn subagents foreground or background, sharing tools/codebase context with the parent; gated behind a "Subagents (Preview)" toggle. *(windsurf.md Sub-agents section; docs.devin.ai/desktop/devin-local)*
- **Antigravity** — `invoke_subagent` tool spawns research/browser/self built-in types; inherits parent's safety config but NOT conversation history; hard 10-level nesting cap. *(antigravity.md §7; antigravity.google/docs/subagents/)*
- **VS Code** — Custom agents declare an `agents` frontmatter field for delegation plus a `handoffs` field for guided sequential workflow transitions; `context:fork` skill option offers narrower isolated delegation. *(vscode.md §7)*

**Not supported / limited by:**
- **Cross-vendor** — Whether a subagent inherits the parent conversation's history is a genuine, unresolved fork — Claude Code's fork mode inherits everything verbatim, Antigravity explicitly does not, Cursor/Codex/Windsurf start fresh — a vendor-neutral "delegate this" primitive cannot assume either. *(comparison.md Sub-agents and delegation section)*
- **Cross-vendor** — Nesting-depth caps vary by an order of magnitude (Cursor 1 level, Claude Code 3, Antigravity 10) and both Cursor and Codex independently document a token-cost multiplier for parallel subagent runs. *(comparison.md Sub-agents and delegation section)*
- **Codex** — ChatGPT Work's hosted subagents don't expose local sandbox/approval controls at all. *(codex.md §14)*

**Depends on this (from the 44 technologies):** Jest, Vitest, Playwright, Docker, GitHub Actions (CI/CD), React, Next.js, Vue, Nuxt, Angular — test/build/frontend technologies where isolating a long-running sub-task (a test suite, a build) from the main conversation is valuable.

---

## 9. Semantic/RAG-based repository search (standing index)

**What it is.** A persistent, pre-built embeddings/vector index (or a server-side semantic index) of the repository that the agent queries directly, as opposed to purely agentic grep/read tool calls issued fresh each turn.

**Supported by:**
- **Cursor** — Documents both semantic ("by meaning") search and a separate "Instant Grep" trigram index; the older embeddings+Merkle-tree architecture's current status vs. Instant Grep is not fully confirmed. *(cursor.md §5; cursor.com/docs/agent/tools/search)*
- **Windsurf/Devin** — Entire local codebase indexed and retrieved via RAG using a proprietary technique ("M-Query"); enterprise remote (server-side) indexing option for GitHub/GitLab/Bitbucket repos. *(windsurf.md Context and context loading section; docs.devin.ai/desktop/context-awareness/overview)*
- **VS Code** — Semantic index (`#codebase`) — GitHub-hosted repos indexed server-side by GitHub, Azure DevOps repos indexed automatically, other workspaces get a locally-built index; claims scaling from 5 to 500,000 files with no stated hard ceiling. *(vscode.md §5; code.visualstudio.com/docs/agents/reference/workspace-context)*

**Not supported / limited by:**
- **Claude Code** — No standing embedding index documented; repository understanding is achieved via agentic Grep/Glob/Read/LSP tool calls only. *(claude-code.md §5; code.claude.com/docs/en/tools-reference)*
- **Codex** — No RAG/embedding-based repo index documented; understanding is via model-issued file reads/shell commands (e.g. `git status`, `ls`) rather than a pre-built index. *(codex.md §3, §5)*
- **Antigravity** — Retrieval mechanism for context selection is not spelled out on any directly-fetched official page; conflicting unofficial third-party claims about cross-repo aggregation. *(antigravity.md §3)*
- **MCP itself** — No repo-indexing primitive at all; the coarse Roots filesystem-hint primitive is itself deprecated as of the 2026-07-28 spec revision. *(mcp.md §5)*

**Depends on this (from the 44 technologies):** React, Next.js, Vue, Nuxt, Angular, TypeScript, GraphQL, Three.js — technologies whose skills tend to involve large codebases where semantic (as opposed to purely literal) lookup would help most.

---

## 10. Persistent memory across sessions

**What it is.** An agent-maintained store of facts, preferences, or decisions that survives beyond a single conversation and is at least partly auto-loaded into future sessions, distinct from a human-authored rules/instructions file.

**Supported by:**
- **Claude Code** — "Auto memory" — Claude-authored, typed (user/feedback/project/reference), per-repo index plus topic files; subagents can additionally get their own separate memory. *(claude-code.md §6; code.claude.com/docs/en/memory)*
- **Codex** — Opt-in "memories" feature, per-user (not per-project), stored locally under `~/.codex/memories/`, explicitly separate from ChatGPT-web/cloud memory. *(codex.md §6; learn.chatgpt.com/docs/customization/memories)*
- **Windsurf/Cascade** — Auto-generated, per-workspace memories, not team-shared, don't consume credits (legacy Cascade agent only). *(windsurf.md Memory section; docs.devin.ai/desktop/cascade/memories)*
- **Antigravity** — "Knowledge Items," auto-distilled by a dedicated background Knowledge Subagent after every conversation, stored under `~/.gemini/antigravity/`, auto-loaded into new conversations. *(antigravity.md §6; antigravity.google/blog/introducing-google-antigravity)*
- **VS Code** — A three-tier (user/repository/session) memory tool exists in preview but is only weakly sourced — no canonical dedicated doc page was found confirming its current details. *(vscode.md §6)*

**Not supported / limited by:**
- **Windsurf/Devin Local** — The new default agent explicitly does NOT support memories at all — an active, ongoing removal, not a hypothetical gap. *(windsurf.md Memory, Limitations sections)*
- **Cursor** — Had a "Memories" beta; the docs URL that used to host it now resolves to the Rules page; community reports describe it being removed/de-emphasized in the 2.x line — current status could not be confirmed either way. *(cursor.md §6)*
- **MCP itself** — No memory primitive at all, by design — entirely a server-implementation convention if a server chooses to provide one. *(mcp.md §6)*
- **Antigravity** — A third-party (Mem0) vendor blog claims the Antigravity CLI specifically has no native persistent memory, in apparent tension with the official desktop-app documentation — even within one vendor, surfaces disagree. *(antigravity.md §6)*
- **Codex** — Local memories and ChatGPT-web/cloud memories are explicitly separate, non-interoperating stores. *(codex.md §14)*

**Depends on this (from the 44 technologies):** Drizzle ORM, Prisma, TypeORM, Mongoose, Tailwind CSS, shadcn/ui, MUI (Material UI) — ORM and design-system technologies where remembering prior schema/theming decisions across sessions would be most valuable.

---

## 11. Permission/approval model for risky operations

**What it is.** A rule-based gate — typically allow/ask/deny with a stated precedence order — sitting between the model's decision to act and actual execution of a risky action (shell command, file write, network call, MCP tool call).

**Supported by:**
- **Claude Code** — deny→ask→allow, first-match-wins, deny always wins regardless of specificity; multiple modes (default/acceptEdits/plan/auto/dontAsk/bypassPermissions). *(claude-code.md §4; code.claude.com/docs/en/permissions)*
- **Cursor** — Tiered: reads/searches/ordinary edits unapproved; sensitive data, config changes, all terminal commands, and all MCP calls require approval; Run Modes modulate autonomy. *(cursor.md §4; cursor.com/docs/agent/security)*
- **Codex** — Two-layer model: sandbox (filesystem/network) plus `approval_policy` (when to pause and ask), with a granular per-category object including `skill_approval` and `mcp_elicitations`. *(codex.md §5, §11; learn.chatgpt.com/docs/permissions)*
- **Windsurf/Devin Local** — Deny/Ask/Allow rules scoped independently to file reads, file writes, command execution, HTTP fetches, and MCP tool calls; deny checked first, ask always prompts, allow only if nothing else matched. *(windsurf.md Permission model section)*
- **Antigravity** — Unified permission engine, deny > ask > allow, resources formatted as `action(target)` across six scoped action types. *(antigravity.md §4; antigravity.google/docs/permissions/)*
- **VS Code** — Generic per-tool confirmation unless a tool implements a custom confirmation message; "Always Allow" escape; a global auto-approve checkbox. *(vscode.md §4)*

**Not supported / limited by:**
- **Cross-vendor** — Every vendor that discusses this explicitly self-describes the system as best-effort/not a guarantee — Cursor: "not a security guarantee"; Claude Code: Bash argument-restriction documented as bypassable; Codex: sandbox doesn't cover web/connectors/MCP/browser. *(comparison.md Tools and tool calling, Agent-specific limitations sections)*
- **VS Code** — Global auto-approve is documented as all-or-nothing with no per-tool granularity — confirmed as an open, unaddressed GitHub issue (microsoft/vscode#269610). *(vscode.md §14)*

**Depends on this (from the 44 technologies):** Docker, GitHub, Drizzle ORM, Prisma, TypeORM, Mongoose, GitHub Actions (CI/CD), Google AdSense — technologies where an unapproved action (a destructive migration, a push, a container run, a live ad-serving change) would be materially risky.

---

## 12. Reciprocal MCP server capability (agent exposing itself as an MCP server)

**What it is.** Whether the coding agent can itself be launched as an MCP server, so other MCP clients/orchestrators can drive it as a callable tool — relevant to chaining or embedding one agent's capabilities from within another automation.

**Supported by:**
- **Claude Code** — `claude mcp serve` exposes Claude Code's own capabilities over stdio to other MCP clients (e.g. Claude Desktop). *(claude-code.md §10; code.claude.com/docs/en/mcp)*
- **Codex** — `codex mcp-server` exposes Codex as an MCP server, explicitly documented as experimental. *(codex.md §10; learn.chatgpt.com/docs/extend/mcp)*

**Not supported / limited by:**
- **Cursor, Windsurf/Devin, Antigravity, VS Code** — No documented equivalent found in any of the fetched pages for these ecosystems during this research pass — the comparison synthesis calls this "not universal." *(comparison.md MCP support section)*

**Depends on this (from the 44 technologies):** None listed in the data — this capability's `relevantTechnologies` list is empty. It is a meta/orchestration capability (agent-to-agent chaining) rather than one tied to a specific technology stack, which is consistent with it having no technology dependents in the data.

---

## 13. Git/GitHub integration and PR automation

**What it is.** Agent-level awareness of git/repo state and the ability to create commits, branches, or pull requests as part of a task, distinct from generic shell access to the `git`/`gh` binaries — and, separately, whether any ecosystem documents integration with GitHub Actions specifically.

**Supported by:**
- **Cursor** — Background/Cloud Agents run on a dedicated VM and branch, and "can automatically open a pull request when done." *(cursor.md §7; cursor.com/help/ai-features/background-agents)*
- **Codex** — Codex cloud is triggerable from GitHub/GitLab/Linear/Slack; OpenAI's public skills catalogue includes a `gh-address-comments` skill implying built-in GitHub-comment workflows. *(codex.md intro, §1; github.com/openai/skills)*
- **Claude Code** — A git-status snapshot is loaded into context at session start; EnterWorktree/ExitWorktree tools support worktree-isolated subagent work on separate branches. *(claude-code.md §3, §7)*

**Not supported / limited by:**
- **Cross-vendor [Synthesis — checked across all seven docs, no mentions found]** — No ecosystem doc researched documents a first-class, named "GitHub Actions" integration (triggering or reading CI workflow runs) as a distinct capability — this is a genuine gap in the underlying research, not a confirmed absence, and should be re-verified before a skill assumes any agent can natively drive GitHub Actions beyond generic shell/gh-CLI access.
- **Most ecosystems** — Outside Cursor's Background Agents and Codex's cloud/hosted surfaces, git/GitHub actions route through the generic shell tool plus the standard permission gate rather than a purpose-built PR-creation feature. *(cursor.md §7; codex.md intro)*

**Depends on this (from the 44 technologies):** GitHub, GitHub Actions (CI/CD), Husky — the version-control and hooks technologies directly implicated by this capability.

---

## What this means for skill design

The data's `crossCuttingNotes` are the most direct source for this section; each point below is drawn from them, tied back to the specific capability tables above where useful.

### Reasonably portable today

- **Metadata + Markdown body.** Only a skill's name/description/instructions content is guaranteed-portable across all seven ecosystems. Everything execution-related is a vendor-specific extension in at least one ecosystem and must degrade gracefully, not fail outright, where unsupported. *[comparison.md Portability requirements #1]*
- **"Commands" and "skills" are converging.** At least three vendors (Claude Code, Codex, Cursor) are actively merging custom commands/prompts into their Skills mechanism, so a skill author should design for the merged model rather than assuming a split between "slash commands" and "skills" will persist. *[comparison.md Portability requirements #6]*
- **[Synthesis: combining the Shell/command execution table (§1, supported by all 7 ecosystems) with the Persistent filesystem/repo write access table (§5, supported by all 7 ecosystems)]** — Skills whose only execution need is "run a CLI command and edit files in the workspace" (e.g. skills wrapping Go, Python, TypeScript, Vite, Jest/Vitest run via CLI, or Husky hook file authoring) rest on the two capabilities with the most uniform, no-exceptions support across every researched ecosystem, making them the safest category to build without per-agent adapters — though even here, enforcement of any sandbox boundary is universally self-described as best-effort (§1, §11), so a skill should not assume sandboxing itself is a security guarantee, only that the *tool* exists everywhere.

### Needs a fallback path, not a hard dependency

- **No standing semantic index.** Roughly half the ecosystems researched (Claude Code, Codex, and possibly Antigravity) rely purely on agentic grep/read-style tool calls instead of a standing RAG index. A skill that assumes fast semantic lookup over a large codebase — relevant to React/Next.js/Vue/Nuxt/Angular/TypeScript-heavy skills per §9's technology list — must have an agentic-search fallback. *[comparison.md Portability requirements #3]*
- **No guaranteed cross-session memory.** This is the least standardized dimension researched, with Windsurf actively removing it from its new default agent (Devin Local) and Cursor's status unconfirmed. A skill with a hard cross-session-memory dependency — e.g. remembered ORM schema decisions (Drizzle/Prisma/TypeORM/Mongoose, §10) or design-system conventions (Tailwind CSS/shadcn/ui/MUI, §10) — has no guaranteed portable target today. *[comparison.md Portability requirements #2]*
- **No fixed hook fail-open/fail-closed default.** Skills relying on hooks to enforce something CI-like ("block this commit unless Jest/Vitest/Playwright passes," directly implicating §7's technology list of Husky, GitHub Actions, Jest, Vitest, Playwright) must not inherit whichever default the target agent ships — Cursor's own docs flag fail-open-by-default as a live, unresolved, security-relevant choice. A skill author must state the fail-open/fail-closed assumption explicitly. *[comparison.md Portability requirements #4]*
- **No fixed subagent history-inheritance behavior.** Skills that delegate a subtask (e.g. running a test suite or build in isolation, §8's technology list of Jest/Vitest/Playwright/Docker/CI plus the frontend frameworks) cannot assume subagents share or don't share the parent's conversation — Claude Code inherits everything verbatim, Antigravity inherits nothing, others start fresh. A vendor-neutral "run this in isolation" primitive must let the skill author declare which behavior it needs, if the target even supports the distinction. *[comparison.md Portability requirements #5]*

### Needs heavy per-agent adapters, or may not be executable at all

- **Docker/container orchestration is not a first-class primitive anywhere.** Per §2, no ecosystem documents the agent invoking `docker build`/`docker run` as a distinct capability separate from shell access — it is plain shell wrapping the docker CLI everywhere it exists at all, and is entirely absent (as a documented capability) from Claude Code, Cursor, and Windsurf/Devin. Skills targeting Docker, or the containerized databases (PostgreSQL, MySQL, MongoDB, Redis, ClickHouse, OpenSearch per §2's technology list), should assume shell-wrapped docker CLI calls, not a managed container primitive, and verify docker availability per target rather than assuming it.
- **Browser automation is missing entirely in Claude Code and Windsurf/Devin.** Per §3, a skill built around Playwright verification, or visual checking of any rendered-UI technology (React, Vue, Angular, Next.js, Nuxt, Three.js, shadcn/ui, MUI, Tailwind CSS, HTML, CSS, Sass), cannot assume native browser control exists — Claude Code would need an external MCP server (e.g. a Playwright MCP server) bridging the gap, and even Codex's browser tools are community-reported as inconsistently exposed.
- **MCP config format is not portable even where MCP itself is supported everywhere.** Per §4, Codex's TOML-based config is a genuine serialization-format incompatibility (not just a path difference) versus every other ecosystem's JSON-based config — a skill declaring "needs a Postgres/Redis/Mongo MCP server" cannot ship one config file; it needs per-target config generation.
- **Untrusted-project trust gating silently narrows capability.** Codex disables project config/AGENTS.md/skills for untrusted projects; Claude Code requires workspace trust before project-scoped MCP servers load; Cursor's workspace trust is off by default. A skill that depends on a database MCP server or a hook firing cannot assume that dependency is actually active in an untrusted workspace. *[comparison.md Portability requirements #7]*
- **[Synthesis: combining the Reciprocal MCP server capability table (§12, supported only by Claude Code and Codex-experimental) with the Git/GitHub integration table (§13, no ecosystem documents a first-class GitHub Actions integration)]** — Two capabilities that a "meta" skill-orchestration or CI-triggering skill might assume exist as agent-native features are actually the two thinnest-supported capabilities in this entire map: only 2 of 7 ecosystems can be driven as an MCP server themselves, and zero ecosystems document native GitHub Actions triggering/reading. A skill that wants to (a) let one agent invocation drive another, or (b) natively read/trigger CI runs, should treat both as requiring external tooling (a `gh` CLI wrapper, a custom MCP bridge) rather than a built-in agent feature, in every ecosystem researched.
- **Tool/capability names are never portable.** No two ecosystems share a tool vocabulary for shell execution, file edits, browser control, or MCP access. Any "this skill needs Docker/Playwright/a Postgres MCP server" declaration must be expressed in vendor-neutral terms and resolved per-target by an adapter, never as a literal tool name. *[comparison.md Portability requirements #9]*
- **No single capability-discovery surface exists.** Skills + rules + subagents + hooks + MCP tools all have separate, per-mechanism discovery surfaces in every ecosystem researched. A skill that needs to check at runtime whether a required capability (e.g. Docker access, a specific MCP server) is actually present cannot rely on one unified introspection call existing anywhere. *[comparison.md Portability requirements #8, Capability discovery section]*
- **Permission/sandbox enforcement is universally young and self-disclosed as incomplete.** Every vendor that documents its own permission or sandbox layer volunteers, unprompted, that it has known gaps or is "best-effort," not a hard security boundary. A vendor-neutral skill spec should not lean on any one vendor's enforcement model as a dependable primitive for gating a skill's genuinely risky operations — destructive DB migrations (PostgreSQL/MySQL/MongoDB/etc. per §11's technology list), GitHub pushes, or container execution. *[comparison.md Agent-specific limitations section]*
- **The same Adapter-layer pattern applies to execution, not just config.** Shell sandboxing, Docker, browser automation, and network defaults follow the same Adapter requirements pattern as the config/format dimensions already documented in the technology knowledge map — path/location mapping, tool-declaration mapping, and trust/precedence mapping all need a translation layer specific to each target ecosystem's actual sandbox and network-access implementation, not just its file conventions. *[comparison.md Adapter requirements section]*

---

## Coverage gaps in the underlying research

- **GitHub Actions integration** is a confirmed absence across all seven ecosystem docs, but the data itself flags this as "a genuine gap in the underlying research, not a confirmed absence" that "should be re-verified before a skill assumes any agent can natively drive GitHub Actions beyond generic shell/gh-CLI access" (§13). This map repeats that caveat rather than treating the absence as settled fact.
- **Reciprocal MCP server capability** (§12) has no linked technologies in the data at all (`relevantTechnologies: []`) — the underlying research judged it a pure meta/orchestration capability, not tied to any of the 44 technologies. This is reported as-is rather than inferring technology links that were not in the source data.
- **Antigravity's memory and retrieval mechanisms** are internally contradictory within the data itself: the official desktop-app docs describe auto-distilled "Knowledge Items" persistent memory (§10), while a third-party Mem0 vendor blog claims the Antigravity CLI specifically has no native persistent memory (§10) — and separately, Antigravity's repository-retrieval mechanism "is not spelled out on any directly-fetched official page," with only "conflicting unofficial third-party claims about cross-repo aggregation" available (§9). Both tensions are preserved above rather than resolved, since the underlying research did not resolve them.
- **Cursor's Memories feature** status is explicitly unconfirmed — the docs URL that used to host it now redirects to the Rules page, and community reports of removal/de-emphasis in the 2.x line could not be verified either way (§10).
- **Windsurf/Devin Local's hook support** is explicitly marked unclear in the source data ("unclear whether Devin Local... supports hooks at all," §7) — this map does not resolve that uncertainty.
