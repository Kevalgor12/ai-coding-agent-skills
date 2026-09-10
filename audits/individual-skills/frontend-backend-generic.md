# Individual quality review — Frontend & Backend generic (Layer 3)

Batch: `frontend-architecture`, `styling-systems`, `ui-ux-design`, `web-accessibility`,
`api-design`, `authentication-authorization`, `backend-architecture`,
`graphql-api-design`, `realtime-communication`.

Reviewed against `core/skill-specification/specification.md` (spec v1.0),
`core/taxonomy/skill-catalog.md` catalog entries (`SK-FE-001..005`, `SK-BE-001..005`),
`skills/code-commenting/SKILL.md`, and `skills/observability/{skill.yaml,SKILL.md}`
as the reference template.

**No files were edited.** Every finding below falls outside the review's
narrow fix-authority list (missing required field / YAML syntax error / CE-1
overflow / `depends_on_skills`-`parents` conflation / VR-5 mismatch / dangling
`related_skills`-`conflicts_with` ID / asymmetric `conflicts_with`) — all nine
skill.yaml files parse cleanly, all required fields are present and well-typed,
no `kind: generic` skill declares `parents`, all `execution_tier`/`required_capabilities`
pairs are internally consistent (Tier A + `file-read`/`file-write` only, for
all nine), `conflicts_with` is empty (and thus trivially symmetric) everywhere,
and every `related_skills`/`conflicts_with`/`depends_on_skills` ID resolves to
a real catalog entry (the `SK-TECH-*` IDs resolve via the technology table at
skill-catalog.md lines ~799–844, not the `###` headers used for generic/discipline
skills — an early false positive in my own search, ruled out by inspection).

## Summary

| Skill | Critical | High | Medium | Low |
|---|---|---|---|---|
| frontend-architecture | 0 | 0 | 2 | 0 |
| styling-systems | 0 | 0 | 0 | 0 |
| ui-ux-design | 0 | 0 | 0 | 0 |
| web-accessibility | 0 | 0 | 2 | 0 |
| api-design | 0 | 1 | 2 | 0 |
| authentication-authorization | 0 | 0 | 1 | 0 |
| backend-architecture | 0 | 0 | 2 | 0 |
| graphql-api-design | 0 | 0 | 2 | 0 |
| realtime-communication | 0 | 0 | 2 | 0 |
| **Total** | **0** | **1** | **13** | **0** |

---

## frontend-architecture (SK-FE-001)

**1. Cross-cutting-concern links point at the wrong file — Medium.**
The `Security`, `Performance`, and `Testing` sections of `skills/frontend-architecture/SKILL.md`
link `security-engineering`, `performance-engineering`, and `testing-strategy` to
`../../core/taxonomy/skill-catalog.md` instead of the sibling skill files
(`../security-engineering/SKILL.md`, `../performance-engineering/SKILL.md`,
`../testing-strategy/SKILL.md`), e.g.:
```
Deep threat modeling is owned by
[security-engineering](../../core/taxonomy/skill-catalog.md).
```
The reference template (`skills/observability/SKILL.md`) and two other skills
in this same batch (`styling-systems`, `ui-ux-design`) use the correct
sibling-path pattern, so this is an inconsistency with the project's own
established convention, not an ambiguous choice. A reader following the link
lands on the 850-line taxonomy catalog instead of the actual cross-cutting
skill content. **Recommendation:** repoint all three links to
`../security-engineering/SKILL.md`, `../performance-engineering/SKILL.md`,
`../testing-strategy/SKILL.md`.

**2. `related_skills` omits the catalog's own related skills — Medium.**
The catalog entry for `SK-FE-001` states `**Related:** SK-FE-002, SK-FE-003, SK-FE-005.`
The skill's actual `related_skills` is `[SK-DISC-002, SK-FE-004, SK-TECH-typescript]`
— it omits `SK-FE-002` (ui-ux-design) and `SK-FE-003` (styling-systems)
entirely, even though the skill's own `scope` text explicitly names
`styling-systems` as an adjacent boundary skill. (`SK-FE-005`/rendering-strategy
is correctly omitted since it isn't yet authored.) **Recommendation:** add
`SK-FE-002` and `SK-FE-003` to `related_skills`.

No other problems found. `depends_on_skills` is empty and correctly so
(specialization by React/Vue/Angular/Next/Nuxt tech skills is not a hard
sub-step); activation/non-activation are disjoint and match the catalog;
the framework security-posture claims (React auto-escaping, Vue/Angular
sanitization defaults, the RSC CVE) all carry inline source markers resolvable
to the cited `technology-decision-matrix.md`/`version-matrix.md`; body is 187
lines, well within CE-2.

---

## styling-systems (SK-FE-003)

**No problems found.** All required fields present and well-typed;
`related_skills` (`SK-FE-002`, `SK-FE-004`, plus the five specializing
technology skills) matches the catalog's `Related: SK-FE-002, SK-FE-004`
line plus the catalog's own `Dependencies: Specialized by SK-TECH-tailwindcss|sass|web-standards|shadcn-ui|mui`;
`depends_on_skills` is correctly empty (specialization ≠ hard dependency);
`Security`/`Performance`/`Testing` sections correctly link to sibling
`SKILL.md` files, matching the observability reference template; the
runtime-vs-build-time-theming and MUI-vs-shadcn/ui distribution-model
framing is factually sound and specific to this skill's scope (not generic
advice); decision framework includes the do-nothing/simplest branch
("fixed brand needs neither" runtime theming machinery); anti-patterns name
a real overengineering trap (adding runtime theming with no actual
theme-switching need). Body is 229 lines.

---

## ui-ux-design (SK-FE-002)

**No problems found.** `related_skills` (`SK-FE-003`, `SK-FE-004`, `SK-TECH-mui`,
`SK-TECH-shadcn-ui`) exactly matches the catalog's `Related: SK-FE-003, SK-FE-004, component-library tech skills`;
the skill is explicit and honest about a real grounding boundary (this
library's research is technology-documentation-shaped, not an independent
UX-research corpus) in both `skill.yaml.scope` and the SKILL.md body, which
is exactly the kind of honest-scope statement the spec's anti-hallucination
rules (SG-3) want; the overlap with `web-accessibility` on native-element
affordances is explicitly disclosed and each skill frames it from a
distinct lens (interaction-design economics vs. accessibility/screen-reader
semantics) with an explicit cross-reference, so this is not duplicated
responsibility. `Security`/`Performance`/`Testing` sections correctly link
to sibling files. Body is 212 lines.

---

## web-accessibility (SK-FE-004)

**1. Cross-cutting-concern links point at the wrong file — Medium.**
Same defect pattern as `frontend-architecture`: the `Security` section links
`security-engineering` to `../../core/taxonomy/skill-catalog.md`, and the
`Testing` section links both `testing-strategy` and the `playwright`
technology skill to the same wrong target, e.g.:
```
Deep test-strategy method is owned by
[testing-strategy](../../core/taxonomy/skill-catalog.md); Playwright-specific
depth is owned by the [playwright](../../core/taxonomy/skill-catalog.md)
technology skill.
```
**Recommendation:** repoint to `../security-engineering/SKILL.md`,
`../testing-strategy/SKILL.md`, and `../playwright/SKILL.md`.

**2. `related_skills` substitutes a catalog-unspecified skill for the
catalog-specified one — Medium.** The catalog's `SK-FE-004` entry states
`**Related:** SK-FE-002, SK-TECH-web-standards, SK-TECH-shadcn-ui, SK-TECH-mui.`
The skill's actual `related_skills` is
`[SK-FE-001, SK-TECH-web-standards, SK-TECH-mui, SK-TECH-shadcn-ui, SK-TECH-playwright]`
— `SK-FE-002` (ui-ux-design) is missing and `SK-FE-001` (frontend-architecture,
not catalog-specified as related here) appears instead. This is a real gap:
`ui-ux-design`'s own body explicitly cross-references `web-accessibility`
("covered in depth by web-accessibility"), but the reverse link is absent,
so the relationship isn't discoverable by following `related_skills` from
this skill outward. **Recommendation:** add `SK-FE-002` to `related_skills`
(keeping `SK-FE-001` is reasonable in addition, not instead).

No other problems found. The skill is notably disciplined about its own
grounding boundary (explicitly declines WCAG-success-criterion-level
conformance claims, both in `skill.yaml` and the body, rather than
fabricating depth this library hasn't researched) — this is a genuine
strength worth preserving, not a finding. Body is 221 lines.

---

## api-design (SK-BE-002)

**1. Stale "not yet authored" claim about `authentication-authorization` — High.**
Both `skill.yaml.scope` and the SKILL.md `Security` section state that
`authentication-authorization` is "not yet authored in this library":
```yaml
# skill.yaml
scope: >-
  ... Not the service's internal
  structure (backend-architecture) or auth mechanics (authentication-authorization,
  not yet authored).
```
```
## Security
... Deep auth mechanics are owned by authentication-authorization (not yet
authored in this library); deep threat modeling is owned by
[security-engineering](../../core/taxonomy/skill-catalog.md).
```
`authentication-authorization` (`SK-BE-005`) is in fact fully authored — it
is one of the nine skills in this very batch, with substantial Security
content of its own. This is a factually incorrect statement that misleads a
consuming agent about the library's actual composition: an agent reading
this text has no reason to believe a dedicated auth-design skill exists to
delegate to, and might improvise auth guidance inline instead of routing
correctly. This is not an architectural change to the skill's scope (the
boundary itself — "auth mechanics belong elsewhere" — is correct and
unchanged) — it's a stale factual parenthetical that needs updating now
that the referenced skill exists. **Recommendation:** in `skill.yaml.scope`,
change `auth mechanics (authentication-authorization, not yet authored)` to
`auth mechanics (authentication-authorization)`; in the SKILL.md `Security`
section, change `authentication-authorization (not yet authored in this
library)` to a proper link, `[authentication-authorization](../authentication-authorization/SKILL.md)`.

**2. Cross-cutting-concern links point at the wrong file — Medium.**
Same pattern as above: `Security`, `Performance`, and `Testing` sections all
link to `../../core/taxonomy/skill-catalog.md` instead of the sibling
`SKILL.md` files. **Recommendation:** as above.

**3. `related_skills` omits the catalog's own related skill — Medium.**
The catalog's `SK-BE-002` entry states `**Related:** SK-BE-005, SK-CONV-006, SK-DATA-001.`
The skill's `related_skills` is `[SK-BE-001, SK-BE-003, SK-TECH-openapi-swagger, SK-DATA-001, SK-CONV-006]`
— `SK-BE-005` (authentication-authorization) is missing, consistent with
finding #1's stale-reference problem. **Recommendation:** add `SK-BE-005`.

No other problems found. The REST-vs-GraphQL decision framework is
genuinely bidirectional (doesn't default to REST), correctly includes the
documented DoS/caching/security-scheme/testing differentiators with inline
source markers, and the escalation rule for a paradigm switch with many
existing consumers is concrete. Body is 172 lines.

---

## authentication-authorization (SK-BE-005)

**1. Cross-cutting-concern link points at the wrong file — Medium.**
The `Performance` section links `performance-engineering` to
`../../core/taxonomy/skill-catalog.md` instead of `../performance-engineering/SKILL.md`:
```
Deep performance method is owned by
[performance-engineering](../../core/taxonomy/skill-catalog.md).
```
Notably, the `Security` and `Testing` sections in this same file correctly
link to `../security-engineering/SKILL.md` and `../testing-strategy/SKILL.md`
— only the `Performance` section has the wrong target, so this is a
one-off slip rather than a file-wide pattern. **Recommendation:** repoint to
`../performance-engineering/SKILL.md`.

No other problems found — this is otherwise the strongest skill in the
batch on the composition-discipline check. The catalog's `SK-BE-005` entry
phrases `SK-QA-002` (security-engineering) as a "Dependency," but the
skill.yaml correctly places it in `related_skills` instead of
`depends_on_skills`: the body text only *references* security-engineering
for general injection/XSS/CSRF/secrets-hygiene topics rather than invoking
it as a hard, blocking sub-step of its own execution, which is exactly the
distinction spec §2.5 draws and exactly the kind of conflation earlier
batches got wrong. `related_skills` (`SK-BE-002`, `SK-BE-003`, `SK-QA-002`,
`SK-DATA-003`) matches the catalog's `Related` line plus its RLS note. The
security content itself is specific and accurate (JWT payloads are signed,
not encrypted; Socket.IO auth must be validated on every reconnect, not
just initial connection; least-privilege-by-default authorization; ORM RLS
capability differs materially between Drizzle/Prisma/TypeORM) — no insecure
recommendations found on the scrutiny this skill's domain warrants. Body is
219 lines.

---

## backend-architecture (SK-BE-001)

**1. Cross-cutting-concern links point at the wrong file — Medium.**
Same pattern: `Security`, `Performance`, and `Testing` sections link to
`../../core/taxonomy/skill-catalog.md` instead of the sibling `SKILL.md`
files. **Recommendation:** as above.

**2. `related_skills` omits the catalog's own related skill — Medium.**
The catalog's `SK-BE-001` entry states `**Related:** SK-BE-002, SK-BE-005, SK-DATA-*.`
The skill's `related_skills` is `[SK-DISC-002, SK-BE-002, SK-BE-003, SK-DATA-001]`
— `SK-BE-005` (authentication-authorization) is missing (the same omission
recurs across four of this batch's five backend skills; see the cross-batch
note below). **Recommendation:** add `SK-BE-005`.

No other problems found. The Fastify-vs-Express framing correctly avoids
citing either side's vendor-published benchmark as an independent ranking
("Vendor-published performance numbers are not independent benchmarks"),
and this is echoed as its own anti-pattern and engineering rule — a good,
concrete example of the anti-tech-bias discipline the spec requires (QR-3).
Body is 197 lines.

---

## graphql-api-design (SK-BE-003)

**1. Cross-cutting-concern links point at the wrong file — Medium.**
Same pattern: `Security`, `Performance`, and `Testing` sections link to
`../../core/taxonomy/skill-catalog.md`. **Recommendation:** as above.

**2. `related_skills` omits the catalog's own related skill — Medium.**
The catalog's `SK-BE-003` entry states `**Related:** SK-BE-005, SK-DATA-002.`
The skill's `related_skills` is `[SK-BE-002, SK-BE-001, SK-DATA-002, SK-TECH-graphql]`
— `SK-BE-005` (authentication-authorization) is missing, despite the
skill's own `Security` section discussing field-level authorization as a
central GraphQL-specific concern. **Recommendation:** add `SK-BE-005`.

No other problems found. The GraphQL-specific technical content is accurate
and appropriately scoped: N+1/DataLoader batching correctly framed as a
correctness requirement rather than an optional optimization; fixed-window
rate limiting correctly called out as insufficient for GraphQL's
variable-cost queries in favor of depth/complexity limits; cursor pagination
correctly preferred as the default idiom over offset/limit; schema evolution
via additive changes + `@deprecated` correctly distinguished from REST-style
versioning. The REST-vs-GraphQL decision itself is correctly *not* re-litigated
here (deferred to `api-design`), satisfying the stated non-duplication
evaluation criterion. Body is 176 lines.

---

## realtime-communication (SK-BE-004)

**1. Cross-cutting-concern links point at the wrong file — Medium.**
Same pattern: `Security`, `Performance`, and `Testing` sections link to
`../../core/taxonomy/skill-catalog.md`. **Recommendation:** as above.

**2. `related_skills` omits catalog-specified related skills — Medium.**
The catalog's `SK-BE-004` entry states `**Related:** SK-BE-005, SK-DATA-004.`
The skill's `related_skills` is `[SK-BE-001, SK-BE-002, SK-TECH-redis]` —
both `SK-BE-005` (authentication-authorization) and `SK-DATA-004` are
missing. The omission of `SK-BE-005` is particularly notable given how much
of this skill's own content is about handshake authentication (an entire
decision-framework branch, an engineering rule, and an anti-pattern are
dedicated to "CORS/Origin checks are not sufficient access control").
**Recommendation:** add `SK-BE-005` and `SK-DATA-004`.

No other problems found. The transport-selection content is precise and
avoids overclaiming cross-tool comparisons (explicitly notes vendor
benchmarks aren't independently verified where relevant); the
backpressure-handling synthesis ("no realtime transport in this dataset has
built-in backpressure — all three independently converge on the same fix
pattern") is a genuinely useful cross-technology synthesis rather than
restated single-source content; the async message-broker/event-streaming
gap is stated explicitly and consistently (in `scope`, `non_activation_conditions`,
Knowledge, anti-patterns, and escalation) rather than answered by
improvisation, which is exactly the honest-scope discipline the spec wants.
Body is 233 lines.

---

## Cross-batch pattern note

Two defects recur across most of the nine skills rather than being isolated
mistakes, which is worth flagging as a pattern rather than nine independent
coincidences:

1. **Wrong cross-cutting-concern link target.** Seven of nine skills
   (`frontend-architecture`, `web-accessibility`, `api-design`,
   `authentication-authorization` [one section only], `backend-architecture`,
   `graphql-api-design`, `realtime-communication`) link `security-engineering`,
   `performance-engineering`, and/or `testing-strategy` to
   `../../core/taxonomy/skill-catalog.md` instead of the sibling skill's own
   `SKILL.md`, inconsistent with the reference template
   (`skills/observability/SKILL.md`) and with two skills in this same batch
   (`styling-systems`, `ui-ux-design`) that do it correctly. This looks like
   a templating/authoring-pass artifact (the same three sentences, with the
   same wrong link target, reused near-verbatim across most of the batch)
   rather than nine independent judgment calls.
2. **`authentication-authorization` missing from `related_skills` where the
   catalog specifies it.** Four of the batch's five `BE-*` skills
   (`backend-architecture`, `api-design`, `graphql-api-design`,
   `realtime-communication`) each have a catalog-specified
   `Related: ... SK-BE-005 ...` line that isn't reflected in the actual
   `related_skills` field, despite each skill's own body substantively
   engaging with auth-adjacent concerns. `authentication-authorization`
   itself is well-composed (correctly uses `related_skills` rather than
   `depends_on_skills` for `security-engineering`), so the gap is
   one-directional — the other four skills don't point back to it.

Neither pattern is a spec validation-rule (VR-*) violation — `related_skills`
existence-checking (VR-3) passes for every ID actually present, and the
wrong links still resolve to a real file, just not the intended one — so
neither blocks the mechanical validator. Both are genuine, fixable content
defects worth a follow-up pass across the batch.
