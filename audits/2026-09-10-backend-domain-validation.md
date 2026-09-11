# Audit: BACKEND-domain skill generation & validation

Date: 2026-09-10. Scope: nine skills — three generic (`SK-BE-001`
backend-architecture, `SK-BE-002` api-design, `SK-BE-003` graphql-api-design)
and six technology skills (`SK-TECH-nodejs`, `SK-TECH-express`,
`SK-TECH-fastify`, `SK-TECH-go`, `SK-TECH-python`,
`SK-TECH-openapi-swagger`). Preceded by a dedicated research pass on Node.js
(missing from the original 44 technologies) and a taxonomy addition
(`SK-TECH-nodejs`). Validated against
[skill-specification](../core/skill-specification/specification.md),
[taxonomy](../core/taxonomy/skill-catalog.md),
[dependency-architecture](../core/dependency-architecture/),
[routing-architecture](../core/routing-architecture/), and
[knowledge-maps](../research/knowledge-maps/)/[technologies](../research/technologies/).

**Scope note:** the user's original 10-item list collapsed to 9 skills after
clarification — "API Architect" and "REST" resolved to the same skill
(`SK-BE-002`, confirmed by the user), and "Node.js" was held pending
dedicated research rather than skipped or guessed at (also per the user's
explicit choice).

**Authorship note:** as with the two prior batches, the three generic skills
were authored directly by hand; the six technology skills were delegated to
parallel agents with pre-verified relationship data and version facts, then
independently re-verified on disk (not trusted from self-reports).

## Pre-work: Node.js research

`research/technologies/nodejs.md` (373 lines, 37 official sources) was
authored via a dedicated agent matching the original 44-technology
methodology exactly, and the four existing registry/index files
(`SOURCE_REGISTRY.md`, `VERSION_REGISTRY.md`, `UNRESOLVED.md`, `README.md`)
were updated to integrate it — verified on disk that none of the 44 existing
entries were disturbed (spot-checked `## Angular` intact; line-count deltas
matched exactly what was reported). `core/taxonomy/skill-catalog.md` was
updated to add `SK-TECH-nodejs` with an explicit "added post-hoc" note.

## Completed skills

| Skill | ID | Files | Citations in SKILL.md |
|---|---|---|---|
| [backend-architecture](../skills/backend-architecture/) | SK-BE-001 | yaml, SKILL.md, 1 reference | 6 |
| [api-design](../skills/api-design/) | SK-BE-002 | yaml, SKILL.md, 1 reference | 7 |
| [graphql-api-design](../skills/graphql-api-design/) | SK-BE-003 | yaml, SKILL.md | 7 |
| [nodejs](../skills/nodejs/) | SK-TECH-nodejs | yaml, SKILL.md | 36 |
| [express](../skills/express/) | SK-TECH-express | yaml, SKILL.md, 1 reference | 38 |
| [fastify](../skills/fastify/) | SK-TECH-fastify | yaml, SKILL.md | 30 |
| [go](../skills/go/) | SK-TECH-go | yaml, SKILL.md | 58 |
| [python](../skills/python/) | SK-TECH-python | yaml, SKILL.md | 24 |
| [openapi-swagger](../skills/openapi-swagger/) | SK-TECH-openapi-swagger | yaml, SKILL.md, 1 reference | 38 |

All nine independently confirmed on disk (file existence, line counts,
directory contents) — not accepted from agent self-reports alone.

**Mechanical checks run and passed, all nine:**
- YAML validity; VR-2 (name/slug/frontmatter match); CE-1 (description ≤ 500
  chars, range 302–496 — `nodejs` and `python` are close to the ceiling but
  compliant).
- VR-8 (body section order matches spec §3.2, subsequence-verified).
- VR-1 (all always-required fields) and technology-conditional fields
  (`parents`, `covered_versions`, `reverify_triggers`, `source_references`)
  present for all 6 technology skills.
- VR-5 (`execution_tier`/`required_capabilities` consistency) — 5 Tier B with
  shell, `openapi-swagger` correctly Tier A (it authors spec documents/static
  tooling config; no shell execution is fundamental to its work, unlike the
  runtime/framework skills).
- VR-3 (every `parents`/`depends_on_skills`/`related_skills`/`conflicts_with`
  ID resolves to a real taxonomy entry) — including the newly-added
  `SK-TECH-nodejs`, confirmed resolvable.
- Conflict-cluster symmetry (`nodejs`⊥`go`⊥`python` as alternative backend
  runtimes; `express`⊥`fastify` as alternative Node frameworks) — no
  asymmetric conflicts found.
- All relative links resolve.

**The `depends_on_skills`-vs-`parents` issue from the DATA-domain batch did
not recur.** All 9 skills correctly have `depends_on_skills: []`, with
specialization captured only in `parents` — verified by direct inspection,
not just agent claims. This is the first batch where every technology-skill
prompt explicitly named the prior mistake and cited the specification's
amended §2.5 rule; the result suggests that fix (rule + explicit warning) is
sufficient and this particular error class is now closed, pending further
confirmation over future batches.

## Unresolved questions

1. **`SK-TECH-nodejs` was added to the taxonomy outside the normal design
   flow** (mid-batch, in direct response to a user-identified gap, rather
   than during the original taxonomy design pass). Its catalog entry is
   marked "added post-hoc" for traceability, but a maintainer should confirm
   this is an acceptable way for the taxonomy to grow, versus requiring a
   separate, dedicated taxonomy-amendment step in the future.
2. **Node.js's research doc has 8 carried-forward unresolved items**
   (exact patch dates, no consolidated breaking-changes index, Corepack's
   roadmap, etc.) — none were load-bearing enough to block the skill, but
   worth a follow-up research pass if Node.js skill usage reveals gaps.
3. **`express` surfaced a genuine research-quality question**: a third-party
   claim of "CVE-2024-51999" tied to a patch release could not be confirmed
   against official Express security pages, and the skill's agent found
   *conflicting* signals on Express 4.x's real support status (official page
   says "Ongoing"; a third-party claim suggests an informal Oct-2026 target
   EOL). The skill correctly asserted only the officially-stated status —
   flagging here since it's a live discrepancy worth watching, not settled.
4. **`go`'s citation count (58) is unusually high** relative to its peers —
   worth a light spot-check that this reflects Go's genuinely rich official
   documentation (plausible; Go's docs are known to be thorough) rather than
   over-citation of restated facts. Not flagged as a defect, just noted for review.

## Duplicated responsibilities

**None found at the engineering-content level**, consistent with the prior
two batches. `express`/`fastify` both explicitly deferred to
`backend-architecture`'s existing Fastify-vs-Express comparison table rather
than restating it; `nodejs` stayed scoped to runtime-only concerns backend-
architecture doesn't cover (event loop, module systems); `graphql-api-design`
and `openapi-swagger` both explicitly declined to restate `api-design`'s
REST-vs-GraphQL and OpenAPI-vs-GraphQL comparison tables, linking instead.

## Missing dependencies

None of the 9 skills reference an unauthored generic parent — this is the
first batch where every technology skill's formal taxonomy parent(s) are
already authored (`SK-BE-001`, `SK-BE-002` both exist). The only forward
references are to `SK-AI-001` (llm-application-engineering, an explicit
research-gap skill per the taxonomy — referenced by `python`) and
`SK-CONV-006` (technical-documentation — referenced by `openapi-swagger`),
both handled correctly as non-fabricated forward references.

## Potential corrections

1. **None required for the recurring `depends_on_skills` issue** — see above;
   the specification fix from the prior audit held across all 9 skills in
   this batch without exception.
2. **`api-design`'s and `graphql-api-design`'s `related_skills` include
   `SK-CONV-006`/`SK-DATA-001`-adjacent forward references** consistent with
   the pattern established in prior batches (reasonable, slightly beyond the
   original taxonomy catalog text, flagged for visibility as before).
3. **The Node.js research-then-taxonomy-then-skill sequence worked as a
   template for handling future "approved list names something ungrounded"
   cases** — worth documenting as the standard procedure (hold batch →
   dedicated research pass matching the 17-dimension methodology → registry
   integration → taxonomy addition → skill authoring) rather than re-deriving
   it ad hoc next time this happens.
4. **No skill in this batch was promoted to `final/`** — same standing gap as
   both prior batches (no executable validator or `evaluations/` tests yet).

## Overall assessment

All nine skills are internally consistent with the specification, taxonomy,
dependency architecture, and routing architecture, well-grounded (24–58
citations per technology skill), and version-aware, including several
genuinely subtle version-sensitive findings correctly surfaced rather than
flattened: Node.js's imminent release-cadence overhaul (v27, annual LTS) and
a real sandbox-escape CVE in its own Permission Model; Express's two
simultaneously-live major lines (4.x still patched, 5.x default); Python's
mid-3.14-series GC revert (3.14.0–4 vs. 3.14.5+ actually differ); Go's
rolling two-majors support window. The specification fix applied after the
prior batch demonstrably closed the `depends_on_skills` conflation issue —
the clearest evidence yet that catching a systemic issue and amending the
spec (rather than only patching instances) compounds across batches.
