# Dependency Graph Audit (Step 29)

Companion to [`cross-skill-audit.md`](cross-skill-audit.md). Covers checks
3 (circular dependencies) and 4 (dependency explosions), the VR-4
layer-monotonicity tension carried over from Step 28, and missing-
dependency findings.

Every number below was extracted from all 86 `skill.yaml` files and
cross-checked against the pre-computed extraction supplied to this step.
The two agree exactly.

---

## The graph, in one table

| Edge type | Count | Skills using it | Max fan-out | Max fan-in |
|---|---|---|---|---|
| `depends_on_skills` (hard composition) | 9 | 5 of 86 | 4 (`code-review`) | 2 (`SK-QA-001`) |
| `parents` (specialization) | 68 | 40 of 86 (all technology skills) | 3 (`nextjs`, `nuxt`, `postgresql`, `redis`) | 6 (`SK-FE-001`) |
| `related_skills` (composition affinity) | 245 | 80 of 86 | 8 (`llm-application-engineering`) | — |
| `conflicts_with` (mutual exclusion) | 32 | 18 of 86 | 3 | 3 |

The complete `depends_on_skills` inventory — five skills, nine edges:

```
SK-CONV-004  refactoring            → [SK-QA-001]
SK-CONV-005  legacy-modernization   → [SK-CONV-004, SK-QA-001]
SK-CONV-007  code-review            → [SK-QA-002, SK-QA-003, SK-CONV-002, SK-CONV-003]
SK-CONV-008  git-workflow           → [SK-CONV-001]
SK-ORCH-003  workflow-composer      → [SK-ORCH-001]
```

---

## Check 3 — Circular dependencies

**None. Confirmed, and I do not dispute it.**

The `depends_on_skills` graph has 9 edges over 8 distinct nodes and is
acyclic. Verified independently by transitive closure; VR-4's acyclicity
requirement holds.

Two adjacent graphs were also checked, because a cycle could hide in them
and neither is covered by VR-4's literal wording:

- **`parents`**: 68 edges, all Layer-4 → Layer-3 (or → Layer-2 in
  `typescript`'s and `husky`'s case). Acyclic by construction — every
  source is a technology skill and every target is generic, so no cycle
  is expressible.
- **`related_skills`**: 245 edges and full of 2-cycles by design
  (`SK-QA-001 ↔ SK-QA-003`, `SK-AI-001 ↔ SK-AI-002`, and 40+ others).
  This is **correct, not a defect**: §2.5 defines `related_skills` as
  "commonly composed-with, not a hard dependency", the dependency
  architecture types it as a *symmetric complementary* edge, and VR-4
  scopes acyclicity to `depends_on_skills` only. Reciprocity is, if
  anything, a quality signal — asymmetric `related_skills` pairs would be
  the smell. Noted so a future reviewer running a naive cycle detector
  over all edge types does not report 40 false positives.

**Nothing to do.**

---

## Check 4 — Dependency explosions

**None in `depends_on_skills`. I agree with the mechanical finding and did
not manufacture one.**

Max fan-out is 4 (`code-review`, which delegates to exactly the four
review facets `taxonomy-analysis.md#classification` says it should).
Max fan-in is 2 (`SK-QA-001`, from `refactoring` and
`legacy-modernization` — both for the same reason, a test safety net).

The more interesting result is the *shape*: **81 of 86 skills declare no
hard dependency at all**, and the 9 edges that exist are concentrated in
Layer 0 and Layer 2. That is not an accident of authoring — it is §2.5's
guidance being followed closely:

> reserve `depends_on_skills` for true hard composition (e.g. a review
> skill that always delegates a security check to `security-engineering`
> as part of its own execution).

The library reserved it correctly. The corollary is D-01 below: **no
Layer-3 skill declares a hard dependency on anything**, even in the three
cases where the catalog says it should.

### Is `related_skills` fan-out the more meaningful explosion signal?

The step brief asked this directly. **Answer: it is the more meaningful
signal for context loading, and by that measure the graph is still not
exploding — but the reason it doesn't is unspecified, which is the actual
finding.**

Top `related_skills` fan-out:

| Skill | Fan-out | Targets |
|---|---|---|
| `llm-application-engineering` | 8 | `SK-AI-002…008`, `SK-QA-004` |
| `database-operations` | 7 | 3 generic + 4 database technologies |
| `styling-systems` | 7 | 2 generic + 5 styling technologies |
| `observability` | 6 | 2 generic + 4 observability technologies |
| `testing-strategy` | 6 | 3 generic + 2 runners + `SK-AI-007` |
| `api-design`, `ci-cd-pipeline`, `containerization`, `deployment-release`, `mongodb`, `mysql`, `performance-engineering`, `postgresql`, `search-integration`, `web-accessibility`, `skill-router` | 5 | — |

Every one of these is a **fan-out to its own specializations**, which is
the honest shape for a Layer-3 hub: `styling-systems` lists the five
styling technologies it can specialize into, `observability` lists its
four. That is a table of contents, not a dependency chain. `redis`'s
appearance in three different parents' related sets (`caching-strategy`,
`realtime-communication`, `search-integration`) reflects genuine
multi-role usage, not sprawl.

The concern is not the number, it is that **`related_skills` has no
routing rule anywhere.** `core/routing-architecture/` mentions the field
zero times across all four of its files. A router could reasonably read
"related" as "also load these," which would turn
`llm-application-engineering`'s 8 into ~36K tokens of bodies for a task
that may need one of them. SR-1 (default-deny) argues against that
reading, and `SK-AI-001`'s own description says it "composes SK-AI-002–008
**selectively**" — so the intent is clear. It is just not written down as
a rule. Carried as **C-01** in [`context-audit.md`](context-audit.md).

**Recommendation:** add one context-selection rule, e.g.
*"CS-9 · `related_skills` is an affinity hint, not a load list. Each
related skill is evaluated by the normal default-deny selection rules on
its own merits; being listed as related is never by itself a reason to
select or load."* One sentence, and it closes the only path by which this
graph could explode.

---

## The VR-4 layer-monotonicity tension

### The finding, confirmed

Exactly **4 edges from 3 skills** point from Layer 2 into Layer 3:

| Source (layer) | Target (layer) | Source's own stated reason |
|---|---|---|
| `SK-CONV-007` code-review (2) | `SK-QA-002` security-engineering (3) | delegated review facet |
| `SK-CONV-007` code-review (2) | `SK-QA-003` performance-engineering (3) | delegated review facet |
| `SK-CONV-005` legacy-modernization (2) | `SK-QA-001` testing-strategy (3) | verification of each increment |
| `SK-CONV-004` refactoring (2) | `SK-QA-001` testing-strategy (3) | the behavior-preservation safety net |

VR-4 says a skill "depends only on same-or-lower layers." These four
violate it. This matches Step 28's `orch-disc-conv.md` finding exactly and
has now been verified by three independent methods.

### Why this is not a per-file mislabeling

Three things make the "just fix the three skills" reading wrong:

1. **The catalog mandates these exact edges.** `skill-catalog.md` states
   them as Dependencies for all three skills (lines 213, 228, 258). They
   were authored to spec.
2. **The prose argues the dependency is genuinely hard.** `refactoring`'s
   scope is literally "Requires a safety net (tests) or explicit
   acknowledgement of its absence," and its workflow invokes
   testing-strategy's method as a blocking sub-step. That is the textbook
   §2.5 definition of `depends_on_skills`. Downgrading it to
   `related_skills` would make the metadata *less* true.
3. **`code-review`'s four edges are one design, not four decisions.**
   `taxonomy-analysis.md#classification` explicitly designs review as "a
   **facet** delivered by several skills rather than one monolith,"
   with code-review aggregating security, performance, quality, and
   comment lenses. Two of those four facets happen to live in Layer 3.
   The other two (`SK-CONV-002`, `SK-CONV-003`) are Layer 2 and pass VR-4
   fine — the same architectural relationship passes or fails purely
   based on where its target was filed.

That last point is the tell. **The violation tracks the taxonomy's
layering, not the relationship's nature.**

### Principal-engineer recommendation

I recommend **Option C** below over the two the brief named.

**Option A — re-layer the QA skills to Layer 2.** Move `SK-QA-001/002/003`
down. Attractive because they *are* universal practice, which is Layer 2's
own definition ("Engineering Conventions (universal practice)"), and it
would make all 4 edges monotone at a stroke.
*Rejected.* It breaks more than it fixes: 9 technology skills declare
`parents: [… SK-QA-00x]`, and `parents` edges would then run Layer-4 →
Layer-2, skipping a layer; `SK-QA-004 observability` would have to move
too or the QA domain splits across two layers; and `security-engineering`/
`performance-engineering` genuinely *are* domain capability skills with
their own knowledge maps, not conventions. The layering is right; the rule
is what is imprecise.

**Option B — add a documented VR-4 exception for cross-cutting QA
delegation.** Carve out "a skill MAY depend on `SK-QA-001/002/003` at any
layer."
*Partly right, but under-general and hard to validate.* It fixes today's
four edges by naming three IDs, which is a hardcoded patch inside a
normative rule. The next skill that legitimately delegates upward
(a `debugging` skill delegating to `observability`, say — see X-01) is not
covered, and someone has to remember to extend the list.

**Option C — restate VR-4 in terms of what it is actually protecting,
and add the invariant it is missing.** Recommended.

VR-4 conflates two guarantees that are separable:

- **Acyclicity** — the real, load-bearing guarantee. Without it,
  composition can loop and a run can't terminate. It holds today (0
  cycles) and should stay a hard `[V]` rule with no exceptions.
- **Layer monotonicity** — a *proxy* for acyclicity, adopted because a
  strict layer order trivially implies no cycles. It is sufficient but not
  necessary, and here it is over-strict: all four violating edges are
  acyclic, intentional, and correct.

Concretely:

> **VR-4a [V]** The `depends_on_skills` graph MUST be acyclic. (No
> exceptions.)
>
> **VR-4b [V]** A `depends_on_skills` edge MUST NOT target a **higher
> layer**, *except* where the target is a **cross-cutting capability
> skill** — one whose `scope` declares it cross-cutting and whose
> `owned_knowledge` is referenced (not copied) by skills across two or
> more domains. Such edges MUST be declared with a `depends_reason` and
> are reported by the validator as a named, reviewable class rather than
> a failure.
>
> **VR-4c [A]** The set of cross-cutting capability skills is a taxonomy
> decision, recorded in `taxonomy-analysis.md`, not asserted per-skill.

This gets three things Options A and B do not: acyclicity stays absolute
and machine-checked; today's four edges become *declared and visible*
rather than silently non-conforming; and the criterion is a property of
the target ("is it cross-cutting?") rather than a list of IDs, so it
extends without editing the rule.

It also has a runtime payoff. `core/orchestrator/self-review.md` R-7
flags that *runtime* layer-monotonicity is unenforced and that a run could
"slowly invert its own layering through accumulated recommendations." An
explicit, enumerated exception set is exactly what an auditor needs to
distinguish "this upward edge is the declared QA-delegation exception"
from "this run has started inverting itself."

**Cost:** a spec edit, a `taxonomy-analysis.md` entry naming
`SK-QA-001/002/003` (and arguably `SK-QA-004`) as cross-cutting, and a
`depends_reason` field on 4 edges. No skill's architecture changes.

---

## D-01 · Three catalog-mandated hard dependencies are declared only as `related_skills` — Medium

The catalog states an unqualified `Dependencies:` for three Layer-3 skills
that the skills themselves declare only as `related_skills`:

| Skill | Catalog says | `skill.yaml` has | VR-4 status if promoted |
|---|---|---|---|
| `SK-DATA-006` data-migration | "Dependencies: `SK-DATA-002`" | `related_skills` only | ✅ same layer (3→3) |
| `SK-BE-005` authentication-authorization | "Dependencies: `SK-QA-002` (security)" | `related_skills` only | ✅ same layer (3→3) |
| `SK-INFRA-003` deployment-release | "Dependencies: `SK-INFRA-002`" | `related_skills` only | ✅ same layer (3→3) |

Every other catalog `Dependencies:` line either matches the skill (the five
skills that do declare `depends_on_skills` all match exactly) or is
explicitly qualified in the catalog itself as "Related X", "Specialized by
X", or "(ideally)" — in which case `related_skills` is the correct home
and there is no drift. So this is three cases, not thirty; the earlier
appearance of ~30 mismatches is an artifact of the catalog's overloaded
`Dependencies:` field (see the cross-cutting observation in the main
audit), not thirty real defects.

**I do not recommend promoting all three.** Assessed individually:

- **`deployment-release → ci-cd-pipeline`: do not promote.** Deploying
  without a pipeline is entirely legitimate (manual deploy, platform
  deploy, `deployment-release`'s own non-activation contemplates it).
  `related_skills` is correct; the catalog line is what is wrong.
- **`authentication-authorization → security-engineering`: do not
  promote.** The two skills already cross-route each other explicitly in
  their non-activation conditions, which is the right mechanism. A hard
  blocking dependency would load the whole security skill for every
  routine login-flow question.
- **`data-migration → orm-integration`: do not promote either** — but see
  D-02, which is the edge that *should* exist and doesn't.

**Recommendation:** correct the three catalog lines to say "Related",
rather than changing three skills to match a field whose semantics predate
the distinction. This is one edit in one file and it removes the drift at
its source.

---

## D-02 · A genuinely missing hard dependency: `data-migration → testing-strategy` — Medium

The strongest kind of missing-dependency finding is a **consistency**
argument, and there is exactly one in this graph.

`SK-CONV-004 refactoring` declares `depends_on_skills: [SK-QA-001]`. Its
stated reason: the operation is only safe if behavior-preservation can be
verified, so the verification method is a blocking sub-step, and where it
is unavailable the skill must say so explicitly rather than proceed. That
reasoning is sound and the edge is right.

`SK-DATA-006 data-migration` has an **identical safety-net requirement**
and declares nothing:

- Its scope is "Migration mechanics and safety." Its `## Escalation` and
  `## Engineering rules` both hinge on reversibility.
- Its verification is "a working rollback path **exists** or its absence is
  explicitly stated" — an existence check, never an execution check.
- Its `related_skills` are `[SK-DATA-001, SK-DATA-002]`. `SK-QA-001` is
  not even related.
- `routing-architecture/examples.md` Example 4 — the worked migration
  routing — explicitly staffs "testing-strategy (migration up/down
  tests)". The routing docs already assume this edge exists.
- The skill has no `## Testing` section at all (X-12 in the main audit).

Two skills with the same safety-net semantics; one declares the
dependency, one has no linkage to testing of any kind. And
`data-migration` is the higher-risk of the two: refactoring a function
badly costs a revert, botching a migration on a populated production
database can cost data.

**Recommendation (human decision, small):** add
`depends_on_skills: [SK-QA-001]` to `data-migration`, mirroring
`refactoring`. It is VR-4-clean (3→3), it makes the graph internally
consistent, and it aligns the metadata with what the routing examples
already do. It should land together with X-12's Testing section, since
they are the same gap seen from two angles. Not applied here because
adding a hard dependency changes routing behavior and belongs to the same
decision batch as D-01.

---

## Summary

| ID | Finding | Severity | Recommendation |
|---|---|---|---|
| — | Circular dependencies | none | — |
| — | `depends_on_skills` explosions | none | — |
| C-01 | `related_skills` has no routing rule | Medium | Add CS-9 (one sentence) |
| VR-4 | 4 upward edges from 3 Layer-2 skills | Medium (inherited) | **Option C** — split VR-4 into acyclicity + a declared cross-cutting exception |
| D-01 | 3 catalog `Dependencies:` lines overstate the edge | Medium | Fix the catalog, not the skills |
| D-02 | `data-migration` missing the safety-net dependency `refactoring` has | Medium | Add `depends_on_skills: [SK-QA-001]` |

**Overall: this is a small, clean, well-controlled graph.** 9 hard edges
across 86 skills, zero cycles, zero explosions, and the one rule it
violates is a rule that is stricter than the property it exists to
protect. The dependency architecture is the healthiest part of this
library.
