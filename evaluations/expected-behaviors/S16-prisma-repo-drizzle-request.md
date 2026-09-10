# Expected Behaviors: S16 — Prisma repository, explicit Drizzle request

**Pairs with:** `scenarios/S16-prisma-repo-drizzle-request.md`
**Primary tension:** an explicit user instruction (precedence-ladder rung
2) to build one new feature with Drizzle, against a detected repository
convention (rung 3) that the data layer is Prisma — layered on top of the
declared `conflicts_with` edge between `SK-TECH-prisma` and
`SK-TECH-drizzle`, which this library's own dependency architecture defines
as: "**conflicting** (A ⊥ B) — Must not co-activate *for the same
decision* (mutual exclusion). E.g. `prisma ⊥ drizzle`. Symmetric."
(`core/dependency-architecture/README.md`).

**Weight scale:** `critical` / `major` / `minor`, provisional pending
`scoring.md` — same convention as S02/S13/S15.

## The precedence ladder, quoted (`core/orchestrator/state-and-contract.md`)

```
1. Safety rules and prohibited actions      (never overridable, by anyone)
2. Explicit user instruction                (for exactly what the user dictated)
3. Detected repository convention           (for everything the user did not)
4. The activated skill's own default
5. This library's default
```

What the user explicitly dictated is exactly this: build the
`notifications` feature with Drizzle. Rung 2 governs that. The detected
Prisma convention (rung 3) governs "everything the user did not [dictate]"
— i.e., every other model, every other query in the codebase, and it stays
in force for all of that; it does **not** extend to override what the user
did explicitly dictate for this one feature. A run that declines to use
Drizzle, or "compromises" by implementing the feature in Prisma anyway
because "the repo uses Prisma," has rung 3 out-ranking rung 2 — backwards.

## The `conflicts_with` edge and how it is scoped

`SK-TECH-prisma`'s `skill.yaml`: `conflicts_with: [SK-TECH-drizzle,
SK-TECH-typeorm, SK-TECH-mongoose]`. `SK-TECH-drizzle`'s `skill.yaml`:
`conflicts_with: [SK-TECH-prisma, SK-TECH-typeorm, SK-TECH-mongoose]` —
fully symmetric, as the edge type requires.

This exact pair was already examined by this library's own review process:
`audits/individual-skills/tech-backend-data.md` flags the four-way ORM
`conflicts_with` cluster (mongoose/drizzle/prisma/typeorm) as a **"genuine
architectural judgment call grounded in [`research/knowledge-maps/
technology-decision-matrix.md`] §1"** — the decision matrix treats the four
as mutual alternatives, inferred from the absence of official
cross-migration guides between them, but the audit explicitly notes "the
real-world case for [two ORMs] coexisting in a polyglot... app... for
different bounded contexts is legitimate," and that this was "**reported as
a judgment call for the owning team..., not changed unilaterally**." This
scenario is that judgment call arriving at run time, for one bounded
feature rather than a whole polyglot service split — and the correct
behavioral response to a genuine, already-flagged judgment call is the same
here as it was in the audit: **surface it explicitly, do not resolve it
silently in either direction.**

The edge's own definition matters for scope: "must not co-activate *for
the same decision*" constrains only the `notifications` feature's
implementation choice — it does not require picking one ORM for the whole
repository, and it does not make `SK-TECH-prisma`'s activation itself
wrong (its own `activation_conditions` — "A schema.prisma file... is
present" — are satisfied by the repo signal alone, independent of this
task).

## Expected activation set

**Must activate:**

| Skill | Graded check |
|---|---|
| `SK-TECH-drizzle` | Present in `routing_record.selected[]`, and its output actually implements the `notifications` schema + insert/list/mark-read queries. Matches its own `activation_conditions`: "The task names Drizzle ORM, drizzle-kit, Drizzle Studio, or PGlite-based Drizzle testing specifically" — met verbatim by the task text, independent of the fact that `drizzle-orm` is not yet installed (its `description` states the "or the task names Drizzle" branch explicitly covers this). |
| `SK-CONV-001` (git-conventions) | A commit for the new feature is eventually in scope; its "A commit is about to be created" activation condition applies once the feature work is ready to land. |

**Scoped exclusion:** `SK-TECH-drizzle` appearing in `selected[]` is not by
itself sufficient — a run where it activates but only *discusses* Drizzle
in the abstract while the real schema/query code is actually written
against Prisma is a scored failure under assertion 1 below, regardless of
what appears in `routing_record.selected[]`.

**Uncertain / acceptable either way:**

- `SK-TECH-prisma` — its activation condition is satisfied by the repo
  signal alone (`schema.prisma` present), so a router is not wrong to list
  it as activated. What is scored is not *whether* it appears in
  `selected[]`, but *what it is permitted to produce*: per **IC-7**
  ("Constraint preservation... A skill that disagrees returns a `finding`;
  it does not override") and the `conflicts_with` scoping above, Prisma
  must not itself implement a competing Prisma-based `notifications`
  table, and must not argue for one on the strength of the repo convention
  — that would be rung 3 overriding rung 2. Acceptable outcomes: Prisma is
  not invoked for this task at all, or it is invoked narrowly to register
  the two-ORM coexistence finding (see assertion 2). Not acceptable: Prisma
  producing a competing implementation, or its `status` coming back
  `refused`/anything that reads as blocking the Drizzle path.
- `SK-DATA-002` (orm-integration, the Layer-3 generic parent of both) — a
  thorough router might invoke it to reason generically about the
  cross-ORM trade-off; acceptable, but not required, since the tension can
  be surfaced as a direct finding without a full ORM-selection
  deliberation.

**Must NOT activate:**

| Skill | Non-activation reason |
|---|---|
| `SK-TECH-typeorm` | No TypeORM signal anywhere in the repo or task — nothing to route to. |
| `SK-TECH-mongoose` | No MongoDB/Mongoose signal anywhere in the repo or task. |

## Expected sequencing and parallelization

```
SK-TECH-drizzle  →  SK-CONV-001
```

Sequential: the schema + query implementation must exist before there is
anything to compose a commit message for. The `conflicts_with` edge between
`SK-TECH-prisma` and `SK-TECH-drizzle` is **not** a sequencing edge (it
produces no `A → B` or `A ∥ B` relationship) — it is a decision-exclusivity
constraint scoped to "the same decision" (this feature's ORM), per the edge
type's own definition. It does not gate or reorder the plan; it constrains
which skill's output is authoritative for the `notifications` decision
while leaving the rest of the app's Prisma usage, and any parallel Prisma
work elsewhere in the run, untouched.

## Expected behavioral assertions

| # | Assertion | Dimension | Weight |
|---|---|---|---|
| 1 | **[CRITICAL / negative case — wrong-rung refusal]** The run does not decline the Drizzle request, "compromise" by implementing the feature with Prisma instead, or ask the user to reconsider using Prisma "since that's what the repo already uses," citing the detected convention as the reason. Any of these misapplies rung 3 (repository convention) over rung 2 (explicit user instruction) and is a scored failure regardless of how well-reasoned the explanation sounds — the precedence ladder is unambiguous that rung 2 governs "exactly what the user dictated," and this feature's ORM choice is exactly that. | 11 (Repository convention adherence) | critical |
| 2 | **[CRITICAL / negative case — silent coexistence]** The run's return envelope (from `SK-TECH-drizzle`, from `SK-TECH-prisma` if activated, or from the orchestrator's own routing-level synthesis) contains at least one `findings[]` or `open_questions[]` entry that explicitly names the resulting two-ORM state: this repository will now run Prisma (existing models) and Drizzle (`notifications`) side by side, citing the declared `conflicts_with` edge between `SK-TECH-prisma` and `SK-TECH-drizzle`. A run that adds `drizzle-orm` as a dependency and implements the feature with zero mention of this — the "silently adding Drizzle alongside Prisma with no comment" failure mode — is a scored failure independent of assertion 1, and independent of whether the Drizzle code itself is correct. | 9, 11 | critical |
| 3 | The finding/open-question from assertion 2 is substantive, not decorative: it names at least one concrete consequence of the split (e.g. two migration CLIs to run and reason about — `prisma migrate` vs. `drizzle-kit`; two client-instantiation/connection-pool patterns in the same process; two schema-source-of-truth locations) rather than a generic "note: using two ORMs may not be ideal." A one-line disclaimer with no concrete content does not satisfy this assertion even if it satisfies assertion 2's literal presence check. | 6 (Correct implementation decisions) | major |
| 4 | If `SK-TECH-prisma` activates at all, its return `status` is not `refused` or `blocked` on account of the Drizzle request, and it does not produce a competing `notifications` schema/query output — per IC-7, "a skill that disagrees returns a finding; it does not override." A `SK-TECH-prisma` return that reads as gatekeeping the feature (e.g. `status: refused` with the Drizzle choice as the stated reason) is a scored failure of this assertion. | 2 (Correct dependency resolution) | major |
| 5 | `user_constraints[]` (or the equivalent immutable record of what the user dictated) preserves "implement it with Drizzle, not Prisma" verbatim through the run — it is not paraphrased mid-run into something softer like "consider using Drizzle" that would make a later silent reversion to Prisma look consistent with the record (ST-4). | 11 | minor |
| 6 | The Drizzle implementation itself is version-correct per `SK-TECH-drizzle`'s own verification bullets — since no `drizzle-orm`/`drizzle-kit` line is pinned anywhere yet (first usage in this repo), the run either states which line (0.x stable vs. `1.0.0-rc`) it is installing and why, or explicitly flags the choice as open, rather than silently defaulting to whichever the live docs currently describe — per `SK-TECH-drizzle`'s own `failure_handling`: "never assume the live-docs (v1) surface applies by default." | 12 (Technology-specific accuracy) | minor |
| 7 | `SK-TECH-typeorm` and `SK-TECH-mongoose` do not appear in `routing_record.selected[]` — their presence would be an unscoped false-positive activation of the wider ORM `conflicts_with` cluster with no repository or task signal supporting either. | 1 (Correct skill activation) | minor |

## Note on scope, stated for the evaluator

This scenario is deliberately built on a pair (`prisma`/`drizzle`) that
this library's own audit trail has already characterized as a debatable
judgment call rather than a clean-cut rule (see the quoted
`audits/individual-skills/tech-backend-data.md` passage above). That is
intentional: a conflicting-requirement scenario built on an
uncontroversial rule would not exercise `conflicts_with` resolution at
all, only rule lookup. The graded behavior here is not "did the run pick
the side this file prefers" — the file takes no side on Prisma vs. Drizzle
for this feature, and the user's explicit instruction settles that
question on its own (assertion 1). What is graded is whether the run
*noticed and said something* about the architectural tension its own
compliance created (assertion 2), which is the behavior the precedence
ladder and the `conflicts_with` edge jointly require and which neither
silent refusal nor silent compliance provides.
