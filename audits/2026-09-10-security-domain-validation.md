# Audit: SECURITY-domain skill generation & validation

Date: 2026-09-10. Scope: two skills, both generic — `SK-QA-002`
security-engineering and `SK-BE-005` authentication-authorization.
Validated against
[skill-specification](../core/skill-specification/specification.md),
[taxonomy](../core/taxonomy/skill-catalog.md),
[dependency-architecture](../core/dependency-architecture/),
[routing-architecture](../core/routing-architecture/), and
[knowledge-maps](../research/knowledge-maps/)/[technologies](../research/technologies/).

**Scope note:** the user's 8-item list ("Application Security,
Authentication, Authorization, API Security, Input Validation, Secrets
Management, Dependency Security, Security Review") maps to 2 skills, not
8 — the taxonomy has exactly two security generics, both already scoped
broadly. "Application Security," "API Security," "Input Validation,"
"Secrets Management," "Dependency Security," and "Security Review" all
collapsed into `SK-QA-002` security-engineering — each is literally named
as a stated responsibility or activation trigger in that skill's own
taxonomy entry ("injection, XSS, CSRF, SSRF, secrets, transport, supply-
chain" as responsibilities; "a security review" as an activation
condition), not a separate skill. "Authentication" and "Authorization"
both map to the single `SK-BE-005` authentication-authorization. There is
no separate security technology skill — security is cross-cutting by
design in this taxonomy, referenced by technology skills rather than
re-documented per-technology. Confirmed via `AskUserQuestion` ("Yes,
proceed with 2") rather than assumed — tying SEARCH's 5→2 as the largest
proportional collapse of this project (8→2).

**Authorship note:** unlike every prior batch, this batch contains **no
technology skills to delegate** — both are cross-cutting generics with no
paired implementation-specific technology skill in the taxonomy (auth/authz
and general security risk categories are referenced by, not specialized
by, individual technology skills). Both were authored directly by hand,
grounded almost entirely in `security-knowledge-map.md`'s full 14-section
breakdown — a document that had already been partially cited piecemeal
across nearly every prior batch (Docker, GitHub Actions, WebSocket/
Socket.IO/WebRTC, OpenSearch, MUI, shadcn/ui, Playwright) but had not yet
been read and synthesized in full for a dedicated consuming skill until
this batch.

## Completed skills

| Skill | ID | Tier | Files | Citations in SKILL.md |
|---|---|---|---|---|
| [security-engineering](../skills/security-engineering/) | SK-QA-002 | A | yaml, SKILL.md, 1 reference | 4 |
| [authentication-authorization](../skills/authentication-authorization/) | SK-BE-005 | A | yaml, SKILL.md | 7 |

Both independently confirmed on disk (file existence, line counts, and
`references/` contents where applicable) — self-authored by hand rather
than delegated, so the "verify against agent self-report" step doesn't
apply this batch; the YAML validity and field-presence checks were still
run and passed on both files, following the same discipline used to catch
defects in delegated work.

**Mechanical checks run and passed, both (scripted, not manual):**
- YAML validity for both `skill.yaml` files.
- VR-1 (all always-required fields present, including `depends_on_skills`
  present-and-empty).
- CE-1 (description ≤ 500 chars) — both well within range.
- VR-2 (SKILL.md frontmatter has exactly the 3 keys `name`/`description`/
  `spec_version`, byte-identical to `skill.yaml`) — verified
  programmatically, zero mismatches.
- VR-3 (every `related_skills`/`conflicts_with` ID resolves to a real
  taxonomy entry) — all resolve cleanly, including the mutual cross-
  reference between the two skills in this same batch and forward
  references to `SK-QA-003` (performance-engineering, unauthored),
  `SK-CONV-007` (unauthored), `SK-DATA-003` (database-operations,
  unauthored, the same standing gap noted in the SEARCH-domain audit),
  and `SK-BE-002`/`SK-BE-003` (both already authored).
- `depends_on_skills: []` for both — no hard sub-step composition needed;
  each references the other via `related_skills` only, since neither
  skill's own procedure literally invokes the other's as an inline
  sub-step (a genuine "these are peers that hand off to each other,"
  not "one composes the other" relationship — correctly distinguished
  from `git-workflow`'s intentional hard dependency on `git-conventions`
  in the prior CONV/INFRA batch).
- All relative links resolve, including the Tier-2 reference file.

## Unresolved questions

1. **The Next.js August 2026 patch's exact CVE identifiers remain
   unverified** — carried into the Tier-2 vulnerability watch list exactly
   as flagged in the source research (sourced from a WebSearch summary,
   not a direct advisory fetch), not resolved or guessed at.
2. **Whether the claim-propagation contract across connection-layer auth,
   RLS-layer role claims, and session-layer identity is documented by any
   single technology in this research is explicitly answered "no"** —
   `authentication-authorization` states this as a structural finding
   (no surveyed technology documents that end-to-end contract) rather than
   implying one exists somewhere unexamined.
3. **ClickHouse's TLS-configuration procedural detail beyond port numbers
   is unconfirmed** in the underlying research (dedicated guides were
   located but not fully fetched) — not asserted as complete in either
   skill.
4. **Mongoose's 8.24.3 `sanitizeFilter` hardening fix's full technical
   scope** (what was previously excluded from `countDocuments`/cursor
   operations) is not fully confirmed from an official page — carried into
   the watch list with that caveat rather than presented as fully
   understood.

None of these four were load-bearing enough to block either skill.

## Duplicated responsibilities

**None found**, and this batch had a real internal duplication risk given
how closely auth and general security overlap in most engineers' mental
model: `authentication-authorization` explicitly defers the general
injection/XSS/CSRF/secrets-hygiene risk categories to
`security-engineering` rather than re-deriving them (stated in both its
scope and its own "Security" section body, which points back to the
sibling skill instead of restating content), while `security-engineering`
explicitly states that auth-specific design questions route to
`authentication-authorization` for depth, only applying its own general
categories where they overlap with auth-adjacent code. Both skills'
`related_skills` cross-reference each other, and neither skill's Knowledge
section restates the other's core content — `security-engineering` covers
secrets/injection/XSS/CORS-CSRF/transport/sandboxing/supply-chain/DoS/
error-handling, while `authentication-authorization` covers session-vs-
token, OAuth2/OIDC, RLS/RBAC, and MFA specifically.

## Missing dependencies

- `security-engineering` references `SK-CONV-007` (unauthored) and
  `SK-QA-003` (performance-engineering, unauthored) in `related_skills`.
- `authentication-authorization` references `SK-DATA-003`
  (database-operations, unauthored — the same standing DATA-domain gap
  first noted in the SEARCH-domain audit and still open) in
  `related_skills`, alongside `SK-BE-002`/`SK-BE-003` (both already
  authored).

Neither skill fabricates content for a missing reference; both are
non-fabricated forward references consistent with every prior batch's
pattern.

## Potential corrections

1. **This is the first batch with no technology skills at all** — a
   direct, correct consequence of the taxonomy's own design (security is
   cross-cutting, referenced rather than specialized by individual
   technology skills). Worth noting as a template for any future batch
   that similarly maps entirely to cross-cutting generics: no agent
   delegation is needed, and the "verify agent self-report" discipline
   simply doesn't apply — the applicable discipline instead is running the
   same mechanical checks (YAML validity, field presence, cross-reference
   resolution) against self-authored work, which this batch did.
2. **`security-knowledge-map.md` had been cited piecemeal across six prior
   batches without ever having a single skill whose job was to synthesize
   it as a whole** — this batch is the first time the full 14-section
   document was read end-to-end for one consuming skill. The resulting
   `security-engineering` skill is denser with cross-technology synthesis
   (7 `[Synthesis: ...]` findings pulled directly into its Knowledge
   section) than most prior generics, which mostly synthesized narrower,
   single-topic research. Worth treating as the reference example for any
   future cross-cutting generic that consumes a full knowledge-map
   document rather than a technology-specific research file.
3. **The CVE/version-bound watch list was deliberately pushed to a Tier-2
   reference file** rather than inlined in `SKILL.md`, since the data is
   dated and explicitly time-sensitive (the skill's own Knowledge section
   states plainly that it must never be presented as permanently current)
   — this is a different Tier-2 rationale than prior batches' "genuinely
   substantial implementation detail" pattern (e.g. `threejs`'s
   breaking-changes table, `sass`'s version history): here the driving
   reason is that the *nature* of the content (a live security posture)
   makes it inappropriate to present inline as settled fact, not just its
   length. Worth naming as a second, distinct legitimate reason for a
   Tier-2 split going forward.
4. **`SK-DATA-003` (database-operations) remains an open DATA-domain gap**,
   now referenced as a forward reference by a second consecutive batch
   (SEARCH, and now this one) — still not blocking anything, but its
   recurrence across batches is worth flagging again as a candidate for a
   future DATA-domain follow-up.
5. **No skill in this batch was promoted to `final/`** — same standing gap
   as all nine prior batches.

## Overall assessment

Both skills are internally consistent with the specification, taxonomy,
dependency architecture, and routing architecture, and unusually
citation-dense in aggregate once the Tier-2 vulnerability watch list is
counted alongside the SKILL.md bodies — the full security-knowledge-map.md
document (14 sections plus a dated CVE table and disclosure-policy
appendix) was read and synthesized in its entirety for the first time in
this project, rather than sampled piecemeal as prior batches' technology
skills had each drawn only the slice relevant to their own tool. The
resulting content correctly surfaces several genuinely load-bearing,
cross-cutting findings that no single prior batch's technology skill fully
captured on its own: the structural blind spot shared by every mainstream
ORM's parameterized-query defense (values are protected, identifiers and
raw-SQL fragments are not); the layered-defense pattern every frontend
framework's own docs push back onto the server/HTTP-header level for XSS;
the distribution-model-determines-blast-radius finding for supply-chain
risk (versioned dependency vs. copy-paste vs. hook-dispatcher); and the
explicit, stated absence of any documented end-to-end claim-propagation
contract across the connection/RLS/session auth layers, which
`authentication-authorization` names as its own design responsibility
rather than assuming it's handled elsewhere. This batch is also the first
with zero technology-skill delegation, a direct and correct reflection of
the taxonomy's own cross-cutting design for security rather than a gap in
coverage.
