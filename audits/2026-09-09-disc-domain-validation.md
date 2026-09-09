# Audit: DISC-domain skill generation & validation

Date: 2026-09-09. Scope: the four Layer-1 Discovery skills generated in this
batch — `SK-DISC-001` requirements-engineering, `SK-DISC-002`
solution-architecture, `SK-DISC-003` technical-planning, `SK-DISC-004`
project-management. Validated against
[skill-specification](../core/skill-specification/specification.md),
[taxonomy](../core/taxonomy/skill-catalog.md),
[dependency-architecture](../core/dependency-architecture/),
[routing-architecture](../core/routing-architecture/), and
[knowledge-maps](../research/knowledge-maps/). This is the **[A] audit pass**;
mechanical **[V]** checks below were run by hand (no validator tool exists
yet — see Unresolved questions #4) and **[E]** evaluations have not been
written (no skill in this batch has passed the full conformance lifecycle to
`final/` yet).

## Completed skills

| Skill | ID | Files | Status |
|---|---|---|---|
| [requirements-engineering](../skills/requirements-engineering/) | SK-DISC-001 | skill.yaml, SKILL.md, references/nonfunctional-requirements-checklist.md | Authored, passes mechanical checks below |
| [solution-architecture](../skills/solution-architecture/) | SK-DISC-002 | skill.yaml, SKILL.md, references/architecture-patterns-and-tradeoffs.md | Authored, passes mechanical checks; see corrections #1 |
| [technical-planning](../skills/technical-planning/) | SK-DISC-003 | skill.yaml, SKILL.md, references/planning-heuristics.md | Authored, passes mechanical checks |
| [project-management](../skills/project-management/) | SK-DISC-004 | skill.yaml, SKILL.md, references/pm-templates.md | Authored, passes mechanical checks |

**Mechanical checks run and passed, all four:**
- VR-2 (`skill.yaml` name/description match `SKILL.md` frontmatter exactly, `slug` matches directory) — verified by diff, exact match all four.
- CE-1 (`description` ≤ 500 chars) — 363 / 462 / 412 / 352 chars respectively.
- VR-8 (body section order matches spec §3.2) — verified by heading extraction; correct fixed order in all four, no skipped/misordered required section.
- VR-5 (`execution_tier` consistent with `required_capabilities`) — 3× Tier A with only `file-read`/`file-write`; project-management Tier C with `git` as the declared non-universal capability and a `capability_fallbacks` entry for it.
- Relative links (`SKILL.md`/`skill.yaml` → `references/…`, `core/…`, sibling skills) — all resolve; none broken.
- VR-3 (cross-referenced skill IDs are valid taxonomy IDs) — all resolve to real taxonomy entries (some to not-yet-authored skills — see Missing dependencies).
- VR-4 (acyclic, layer-monotone composition) — only one hard `depends_on_skills` edge exists in this batch (`solution-architecture → SK-DISC-001`), same layer, no cycle.

## Unresolved questions

1. **Is `depends_on_skills` meant to encode hard or soft dependency?** The
   specification (§2.5) defines it only as "skills this one relies on," without
   distinguishing a hard blocking dependency from a soft "needs this output,
   degrades gracefully if absent" one. This batch surfaced the ambiguity
   directly — see Correction #1.
2. **Should `project-management`'s `activation_mode` be `manual` or `auto`?**
   Set to `manual` here, consistent with the dependency-architecture activation
   matrix authored earlier and the taxonomy's own "scope it modestly" note
   (thin research grounding). An `auto` mode gated on "long-running,
   multi-session effort" is plausible but risks over-triggering without a
   crisper detection signal than currently exists. Left conservative
   pending real usage data.
3. **Does `grounding: mixed` for `solution-architecture` fully satisfy SG-1/
   SG-2, given its `source_references[].url` values are internal repo paths
   (the knowledge-map files) rather than external documentation URLs?** The
   specification's SG-1 wording ("resolve through a `research/…` file to an
   official documentation URL") was written with technology skills in mind,
   where the internal file cites an external primary source. Here the internal
   file *is* the primary source for this skill's decision-support content
   (it's already a citation-preserving synthesis). This reading is defensible
   but wasn't tested against a technology skill in this batch to confirm the
   pattern generalizes — worth confirming when the first `kind: technology`
   skill is authored.
4. **No mechanical validator exists yet.** Every `[V]` check in this audit was
   performed by hand (grep/diff), not by an automated tool. The specification
   assumes such a tool exists; `core/` currently holds only its design. This
   is a real gap in the library's tooling, not a defect in these four skills.

## Duplicated responsibilities

**None found as engineering-responsibility duplication** — the four skills'
scopes were deliberately drawn to be mutually exclusive and each `SKILL.md`
states explicitly where a neighboring concern is *not* its job (e.g.
solution-architecture defers post-decision technology specifics to Layer-4
skills; technical-planning explicitly distinguishes itself from both
project-management and the not-yet-authored `workflow-composer`).

**One specification-level redundancy found**, not a responsibility
duplication but worth flagging alongside it: the
`solution-architecture ← requirements-engineering` relationship is expressed
in two places that could drift apart — the hard `depends_on_skills` field
*and* the softer `required_context`/`failure_handling` fields (which describe
graceful degradation, i.e. a soft dependency). See Correction #1.

## Missing dependencies

These four skills reference (via `related_skills`) five taxonomy skills that
are valid IDs but have no authored `skill.yaml`/`SKILL.md` yet — expected,
since this batch was scoped to exactly the four `SK-DISC-*` IDs, but listed
here per the report requirement:

| Referenced ID | Name | Referenced by |
|---|---|---|
| `SK-CONV-001` | git-conventions | project-management |
| `SK-CONV-005` | legacy-modernization | solution-architecture |
| `SK-CONV-008` | git-workflow | project-management |
| `SK-INFRA-002` | ci-cd-pipeline | project-management |
| `SK-ORCH-003` | workflow-composer | technical-planning |

None of these are load-bearing for the four authored skills to function
correctly on their own — each reference is `related_skills` (complementary),
never a hard `depends_on_skills` edge, so this batch is self-contained and
usable before those five exist.

## Potential corrections

1. **Reconsider `solution-architecture`'s hard `depends_on_skills: [SK-DISC-001]`.**
   The taxonomy itself hedges this as "(ideally)," and this skill's own
   `failure_handling` already describes graceful degradation ("if requirements
   are missing... request them... rather than architecting against
   assumptions") — behavior inconsistent with a hard dependency. Recommend
   moving `SK-DISC-001` out of `depends_on_skills` and into `related_skills`
   only, letting `required_context` + `failure_handling` carry the real
   (soft) relationship. Not corrected in this pass — flagged for a
   maintainer decision, since it also touches Unresolved question #1 (what
   `depends_on_skills` is supposed to mean library-wide) and shouldn't be
   resolved unilaterally for one skill.
2. **`project-management`'s `related_skills` includes `SK-DISC-003`
   (technical-planning), which was not in the original taxonomy catalog entry
   for this skill.** Added because a tracked effort plausibly tracks a
   technical-planning task-plan's steps as issues, and the addition is
   consistent with the rest of the design — but it's a scope addition beyond
   the approved taxonomy text, so it's flagged rather than silently kept.
3. **Security/Performance/Testing as dedicated body sections appear only in
   `solution-architecture`**, not in the other three. This is intentional and
   spec-compliant (per §3.2, those sections are conditionally required only
   when the skill's own execution touches a trust boundary / hot path /
   produces runnable code — none of the other three do), and the brief's
   "consider security/performance/testing" requirement is met via real content
   folded into their `Knowledge` sections instead of padding in an
   otherwise-empty dedicated heading (avoiding the spec's own CE-4/QR-5
   anti-filler rules). Flagged for awareness, not recommended for change —
   forcing empty Security/Performance/Testing headings into these three would
   itself violate the specification.
4. **No "Deployment" body section exists anywhere**, because the specification
   (§3.2) does not define one — deployment considerations were folded into
   `Knowledge`/`Decision framework` content instead (deployment-environment
   constraints in requirements-engineering's non-functional checklist;
   deployment-target reasoning in solution-architecture's decision framework).
   This satisfies the brief's "consider deployment" requirement without
   requiring a specification change, but is worth noting since deployment was
   explicitly named in the brief's behavior list and doesn't have as visible a
   home as security/performance/testing do.
5. **`project-management`'s `References` section doesn't link back to
   `core/taxonomy/` the way the other three do** (a minor consistency gap,
   cosmetic only).

## Overall assessment

All four skills are internally consistent with the specification, taxonomy,
dependency architecture, and routing architecture, and are appropriately
grounded (solution-architecture in the knowledge-map research directly; the
other three in engineering-convention, correctly, since the technology
research doesn't cover requirements/planning/PM methodology). No skill in
this batch is promoted to `final/` — per the specification's conformance
lifecycle, that requires a passing mechanical validator (doesn't exist yet)
and an `evaluations/` test proving each skill's `evaluation_criteria` (not
yet written). Recommend resolving Unresolved question #1 before authoring the
next batch, since it will recur for every skill with a soft "needs this
output but degrades gracefully" relationship to another skill.
