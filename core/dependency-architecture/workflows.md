# Workflow Patterns

Ten canonical task shapes, each a gated composition of skills. Notation:

`→` sequential   `∥` parallel   `[cond]` conditional   `⟳` iterate-until
`⤾` review loop (build→review→fix→re-review)   `⛔` human-approval gate

Every workflow is driven by `skill-router` → `workflow-composer`, with
`capability-adapter` as the barrier before any Tier B/C step. Conventions
(`code-commenting`, `code-quality`, `git-conventions`) attach throughout and are
not repeated at each step. All workflows are **fallback-safe**: a missing
capability degrades a step to advisory rather than failing the workflow.

---

## 1. Greenfield development

New system from nothing.

```
requirements-engineering
  → solution-architecture            (⛔ if a major irreversible tech commitment — confirm)
  → technical-planning
  → [parallel scaffolding]  frontend-architecture ∥ backend-architecture ∥ data-modeling
  → implementation:  domain skills compose their SK-TECH-* specializations
       (FE stack ∥ BE stack when modules are disjoint)
  → testing-strategy  (⟳ test-fix)
  → code-review  ⤾  (delegates security ∥ performance ∥ quality ∥ comment facets)
  → ci-cd-pipeline  →  containerization
  → deployment-release   ⛔ (first production deploy)
```

- **Conditional:** SEO (`[public-web]`), auth (`[trust-boundary]`), realtime
  (`[realtime-need]`), observability (`[production]`).
- **Escalation:** architecture ambiguity ↑ requirements/human; destructive
  infra ↑ human.

## 2. Feature development

Add a feature to an existing system.

```
[requirements-engineering if under-specified]
  → technical-planning
  → implementation (domain + tech skills, following existing architecture)
  → testing-strategy (⟳)
  → code-review ⤾
  → git-conventions + git-workflow  →  PR   ⛔ (posting/merge is outward-facing)
```

- **Skips** greenfield's architecture step unless the feature introduces a new
  architectural concern (then ↑ solution-architecture).
- **Parallel:** review facets; independent files.

## 3. Bug fixing

A known defect to correct.

```
reproduce the defect
  → [debugging workflow → find root cause]      (see #4)
  → minimal fix (smallest change that addresses the root cause)
  → regression test (testing-strategy: add a test that fails before, passes after)
  → code-review ⤾
  → git-conventions (fix/bugfix prefix) + commit
```

- **Anti-overengineering gate:** fix the root cause, not the symptom; no
  opportunistic refactor bundled in (that ↑ refactoring as a *separate* change).

## 4. Debugging (the diagnostic loop)

Distinct from #3 — this is *finding* the cause; #3 *applies* the fix.

```
reproduce
  → ⟳ { hypothesize → instrument/observe (logs, EXPLAIN, breakpoints) → narrow }
       until root cause identified
  ↑ bug-fixing (hand off the confirmed cause)
```

- **Iteration** is the defining semantic. Uses `observability`/tech-specific
  debugging guidance for instrumentation.
- **Escalation:** if the cause is environmental/external (not in the code),
  ↑ human with findings rather than guessing a code change.

## 5. Refactoring

Improve structure, preserve behavior.

```
ensure safety net:  testing-strategy  (if no tests → ⛔/flag the unverifiable risk)
  → ⟳ { small behavior-preserving step → run tests (must stay green) }
  → code-review ⤾  (verify no behavior change slipped in)
  → git-conventions (refactor prefix) + commit
```

- **Hard rule:** no feature/behavior change may ride along; if a bug is found,
  ↑ code-review/bug-fixing as a separate change.
- **Fallback:** no shell to run tests → advisory refactor with an explicit
  "behavior-preservation unverified" caveat.

## 6. Migration

Schema/data or system migration.

```
assess current vs target  (legacy-modernization / data-migration)
  → plan  (expand/contract for zero-downtime; rollback points)
  → implement migration (reversible)
  → verify (up and down paths; data integrity)
  → rollout   ⛔ (destructive or production-affecting step — confirm)
  → monitor (observability) for regressions
```

- **Version-awareness:** consumes per-tech breaking-change data + the
  [version matrix](../../research/knowledge-maps/version-matrix.md).
- **Escalation:** any data-losing step ↑ human.

## 7. Performance optimization

```
measure/profile  (establish the baseline and the dominant cost — evidence, not a guess)
  → ⟳ { change the dominant cost → re-measure } until budget met OR diminishing returns
  → code-review ⤾ (perf facet = performance-engineering)
  → [deployment-release ⛔ if prod]
```

- **Anti-overengineering gate:** refuse to micro-optimize a non-bottleneck; stop
  at the budget. Levers pulled in priority order from the
  [performance map](../../research/knowledge-maps/performance-knowledge-map.md)
  (N+1 → index → cache → bundle → pooling → scale).
- **Iteration** with a measured exit criterion is the defining semantic.

## 8. Security remediation

```
security-engineering: identify + triage (severity, exploitability; CVEs are time-sensitive)
  → fix (highest severity first)
  → verify (re-test the specific vector) ⤾ until the finding is closed
  → [secrets exposed → rotation ⛔ human]
  → [disclosure/outward comms → ⛔ human]
  → deployment-release ⛔ (if prod hotfix)
```

- **Escalation-heavy:** rotation, disclosure, and prod hotfix are all human
  gates. Uses the
  [security map](../../research/knowledge-maps/security-knowledge-map.md)
  CVE watch-list, treated as re-verifiable, not evergreen.

## 9. Legacy modernization

```
assess current vs target state (versions, deprecated patterns)
  → plan incremental (strangler-style; avoid big-bang unless justified)
  → ⟳ per increment: { modernize slice → refactoring → testing-strategy → code-review ⤾ }
  → handle breaking changes per tech skill's documented migration notes
  → [each risky increment ⛔ if it touches prod]
```

- **Builds on #5 (refactoring) and #6 (migration)** as sub-workflows.
- **Version-awareness** is central: `covered_versions` + `reverify_triggers`
  drive which breaking changes apply.

## 10. AI feature development

Build a feature that calls an LLM. **Flagged:** `SK-AI-001` is a research-gap
skill (needs a dedicated research pass before it can be authored honestly).

```
requirements-engineering (incl. eval/acceptance definition — not vibes)
  → llm-application-engineering: design (prompt/context, tool-calling, [RAG → search-integration + vector])
  → implementation (compose data/search skills for retrieval; validate/structure output)
  → ⟳ eval loop: { run eval harness → adjust prompt/tooling } until eval criteria met
  → code-review ⤾  (MUST include security-engineering: prompt-injection, data exfiltration, output trust)
  → [live external LLM call with cost/data implications ⛔ human]
  → deployment-release ⛔ (if prod)
```

- **Distinct semantic:** acceptance is an **eval loop**, not a pass/fail test
  suite — LLM outputs are non-deterministic.
- **Security is mandatory, not optional:** prompt injection and untrusted-output
  handling are first-class review facets here.

---

## Cross-workflow execution-semantics summary

Consolidating the brief's six determinations across all workflows:

| Determination | Where it appears |
|---|---|
| **Must run sequentially** | discovery chain (requirements→architecture→planning); data-modeling→orm/migration; build→review; ci→deploy; capability-adapter barrier before any Tier B/C step. |
| **Can run in parallel** | review facets; disjoint module builds; read-only analyses; fan-out over disjoint files; independent audits (SEO ∥ a11y). Offered, degraded to sequential where the host lacks sub-agents. |
| **Conditional** | all Layer-3/4 skills (domain/tech present); SEO (public web), auth (trust boundary), realtime (realtime need), observability (production), migration destructive-step handling. |
| **Require iteration** | debugging (root-cause loop), performance (measure loop), refactoring (small-step loop), testing (test-fix), legacy (per-increment), AI (eval loop). |
| **Require review loops** | every workflow's `code-review ⤾`; security remediation's verify loop. |
| **Require human approval** | destructive migration, history rewrite/force-push, production deploy/release, outward-facing posts/sends, secret rotation, terms/OAuth/credentials, cost/data-bearing live LLM calls. |

Every workflow is a specific ordering over the same edge set in the
[dependency graph](dependency-graph.md); the [matrices](matrices.md) are the
lookup tables that make each ordering decision (parallel? conflict? escalate?)
mechanical rather than ad hoc.
