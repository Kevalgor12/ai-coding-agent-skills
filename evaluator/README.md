# Evaluator — Behavioral Evaluation Runner

Vendor-neutral behavioral evaluation runner for the AI Coding-Agent Skill Library.
Evaluates real agent behavior against observable outcomes rather than prose similarity.

## Architecture

```
Skill → Evaluation Scenario → Expected Behaviors → Agent Adapter
    → Isolated Fixture Repo → Real Agent Execution → Observed Behavior
    → Behavioral Scoring → Evaluation Report → Promotion Decision
```

### Modules

| Module | Role |
|--------|------|
| `config.py` | Paths, constants, thresholds |
| `models.py` | Data model (14 dataclasses: Scenario, Assertion, RunRecord, ScenarioScore, ...) |
| `loader.py` | Parse scenario Markdown + assertion YAML + expected-behaviors tables |
| `checker.py` | Evaluate individual AssertionCheck predicates against a RunRecord |
| `scorer.py` | Combine check results into AssertionVerdicts → ScenarioScore |
| `promotion.py` | Evaluate promotion gate requirements for a skill |
| `reporter.py` | Write structured JSON + Markdown results |
| `coverage.py` | Compute skill coverage across all 88 skills |
| `run.py` | CLI entry point |
| `adapters/base.py` | Abstract AgentAdapter interface |
| `adapters/mock.py` | Mock adapter (returns scripted RunRecord) |
| `adapters/claude_code.py` | Claude Code adapter (runs `claude` CLI) |
| `assertions/S*.yaml` | Machine-checkable predicate definitions for all 16 scenarios |
| `tests/` | Test suite (59 tests) |

## How to Run

```bash
# Run one scenario with mock adapter (no live agent needed)
python3 evaluator/run.py --scenario S01 --adapter mock

# Run all 16 scenarios with mock adapter
python3 evaluator/run.py --adapter mock

# Run with Claude Code (requires claude CLI in PATH)
python3 evaluator/run.py --scenario S12 --adapter claude-code

# Coverage report only
python3 evaluator/run.py --coverage

# Promotion gate check for one skill
python3 evaluator/run.py --promote SK-DB-001 --adapter mock

# Machine-readable JSON output
python3 evaluator/run.py --adapter mock --json
```

Results are written to `evaluations/results/`.

## How to Add a New Evaluation Scenario

1. Write `evaluations/scenarios/SNN-description.md` following the existing format:
   - Task text
   - Repository signals
   - Expected activation set (must_activate / must_not_activate / acceptable_either)
   - Expected sequencing and parallelization

2. Write `evaluations/expected-behaviors/SNN-description.md` with:
   - An assertion table: `| # | Assertion | Dimension | Weight |`
   - Weights must be `critical`, `major`, or `minor`

3. Write `evaluator/assertions/SNN.yaml` with machine-checkable predicates:
   ```yaml
   assertions:
     - number: 1
       description: "Short label"
       evaluation_method: observation  # or human_review, structural
       checks:
         - type: routing_contains
           skill_id: SK-EXAMPLE-001
   ```

4. Optionally add a fixture skeleton under `evaluator/fixtures/SNN/`
   (files the isolated workspace should start with).

## How Expected Behaviors Are Defined

Each scenario has a corresponding `evaluations/expected-behaviors/SNN-*.md` file
containing a Markdown table of assertions. Each assertion specifies:

- **Number** — links to the YAML predicate file
- **Assertion** — prose description of what is expected
- **Dimension** — which of the 15 evaluation dimensions this covers (1–15)
- **Weight** — `critical` / `major` / `minor`

The YAML file in `evaluator/assertions/SNN.yaml` adds machine-checkable predicates
to each assertion number. Prose-only assertions default to `human_review`.

## How Scoring Works

From `evaluations/scoring.md`:

| Weight | Rule |
|--------|------|
| `critical` | One failure → scenario outcome = `failed` |
| `major` | Deduction; ≥ 2/3 must pass for `complete` outcome |
| `minor` | Tracked; does not affect the outcome |

Scenario outcomes:

| Outcome | Condition |
|---------|-----------|
| `complete` | All critical pass AND ≥ 2/3 major pass |
| `partial` | All critical pass, ≥ 1 major fails |
| `failed` | Any critical assertion fails |
| `blocked` | Cannot evaluate any critical assertion (all `not-evaluated`) |

## How Promotion Decisions Work

A skill is eligible for promotion when ALL of these gates pass:

1. **scenario_exists** — at least one scenario must-activates this skill
2. **scenario_executed** — that scenario has been run (non-empty status)
3. **critical_assertions_pass** — no critical assertion fails
4. **no_critical_security_failures** — no critical assertion in dimension 7 (security) fails
5. **major_pass_rate** — ≥ 2/3 of major assertions pass
6. **human_reviewer_signoff** — ≥ 1 human sign-off, or no human_review assertions pending

## Assertion Check Types

| Type | What it checks |
|------|---------------|
| `routing_contains` | `skill_id` in `routing_selected` |
| `routing_excludes` | `skill_id` NOT in `routing_selected` |
| `ledger_contains` | `skill_id` in `ledger` (optional: `status` filter) |
| `command_run` | `pattern` in `commands_run` (optional: `regex: true`) |
| `file_changed` | `path` substring in `files_changed` (optional: `regex: true`) |
| `status_is` | `run_record.status == value` |
| `output_pattern` | regex/substring in `output_text` |
| `no_escalation` | `open_questions` is empty |
| `test_passed` | `VerificationEntry` matching `item` has `status=pass` |
| `human_review` | Always `not-evaluated` — requires a human reviewer |

**Inverted checks** (where finding the pattern means failure) must be handled in
the scenario's assertion notes and interpreted by the human reviewer.
Future work: add a `negate: true` field to `AssertionCheck`.

## Current Skill Coverage

Run `python3 evaluator/run.py --coverage` for current numbers. As of the
initial implementation:

- **40/88** skills have primary coverage (appears in a `must_activate` set)
- **30/88** have boundary coverage (appears in `must_not_activate` or `acceptable_either`)
- **18/88** uncovered (no scenario at all)

Uncovered skills are mostly Layer-4 technology skills for ecosystems not yet
represented in the 16 scenarios (Docker, GitHub Actions, Go, Grafana, etc.).

## Skills Still Blocked (Missing Scenarios)

The following 18 skills have no scenario coverage and cannot receive a
promotion decision:

```
SK-DATA-004   caching-strategy
SK-TECH-docker
SK-TECH-fastify
SK-TECH-github-actions
SK-TECH-go
SK-TECH-grafana
SK-TECH-nextjs
SK-TECH-nuxt
SK-TECH-openapi-swagger
SK-TECH-opentelemetry
SK-TECH-prometheus
SK-TECH-python
SK-TECH-sass
SK-TECH-sentry
SK-ORCH-001   skill-router
SK-FE-003     styling-systems
SK-TECH-typescript
SK-TECH-web-standards
```

To unblock a skill: add a scenario where it must activate (see "How to Add a
New Evaluation Scenario" above).

## Known Limitations

1. **Inverted checks** — assertions like "this pattern must NOT appear in output"
   cannot be expressed as a machine-checkable `fail` condition with the current
   check types. They are marked `human_review` in the YAML `notes` field.
   Planned fix: add `negate: true` to `AssertionCheck`.

2. **Human review required** — 30–40% of assertions require a human reviewer.
   Scenarios cannot achieve an automated `complete` verdict without a human
   sign-off pass. This is by design (the library's own evaluation-spec says
   behavioral correctness cannot be fully automated).

3. **Claude Code adapter structured output** — the adapter currently relies on
   a `<<<EVAL_RUN_RECORD>>>` JSON block in `claude --print` output. Claude Code
   does not natively emit this block; the adapter falls back to heuristic parsing
   when the block is absent, resulting in most assertions returning `not-evaluated`.
   A future pass will instrument the skill invocation with an explicit output
   schema instruction.

4. **Fixture skeletons not yet authored** — the `evaluator/fixtures/` directory
   exists but is empty. The Claude Code adapter runs in the skill directory
   as a fallback. Per-scenario repository skeletons (the minimal repo state
   each scenario's task assumes) should be authored to make runs reproducible.

5. **No parallel scenario execution** — the CLI runs scenarios sequentially.
   A `--parallel` flag and async adapter interface are future work.

## Running the Test Suite

```bash
python3 -m pytest evaluator/tests/ -v
```

Expected: 59 tests, all passing.
