---
name: Data modeling
description: >-
  Design relational or document data models and choose the right store shape
  (relational/document/columnar) for the access pattern. Use when a new data
  model is being designed or an existing one is being changed. Not for query
  optimization on an existing schema, ORM-specific mapping, or migrating a
  populated database — those are separate skills.
spec_version: "1.0"
---

## Purpose & scope

Design the shape of the data: entities, relationships, keys, constraints, and
which kind of store (relational, document, columnar/OLAP, key-value) actually
fits how the data will be read and written. This skill decides *the model*;
it does not tune queries against an existing model (database-operations,
not yet in this library), does not carry ORM-specific mapping mechanics
([orm-integration](../orm-integration/SKILL.md)), and does not evolve an
already-populated schema safely ([data-migration](../data-migration/SKILL.md)).

## When to use / When not to use

**Use** for a new data model, a structural change to an existing one, or an
open question about which store shape fits the workload. **Do not use** for
tuning an existing schema's queries/indexes, for ORM-specific relation-mapping
mechanics once the model is already decided, or for the mechanics of safely
changing a populated production schema.

## Knowledge

**The store-shape decision is not about which database is "best" — it's
about which normalization/consistency trade-off the access pattern actually
needs.** The library's own research across PostgreSQL, MySQL, MongoDB, and
ClickHouse [Source: technology-decision-matrix.md §2] converges on a
synthesized spectrum:

- **PostgreSQL** is built to make heavily normalized, joined, transactional
  schemas fast — full ACID via MVCC, native row-level security, built-in
  full-text search.
- **MySQL** occupies similar relational territory (full ACID via InnoDB) with
  a different operational profile (pluggable storage engines, different auth/
  encryption tooling).
- **MongoDB's own documentation explicitly steers users *away* from
  join-heavy patterns toward embedding** — excessive `$lookup` is called out
  in MongoDB's own docs as a signal the data should be denormalized instead
  [Source: technology-decision-matrix.md §2, "excessive $lookup... anti-pattern"].
  Multi-document ACID transactions exist but are the exception, not the default mode.
- **ClickHouse deliberately abandons general transaction support and
  efficient point-queries/row-updates in exchange for columnar analytical
  scan speed** — an explicit design trade-off in its own docs, not a
  limitation to work around [Source: technology-decision-matrix.md §2,
  "deliberate trade-off: no general transaction support"].

None of these sources make a direct comparative performance claim against
each other — each documents its own tuning levers, not a head-to-head number
[Source: technology-decision-matrix.md §2, "Unresolved"]. Don't present a
"PostgreSQL is faster than MongoDB" style claim as researched fact; it isn't.

**Relational vs. document is a real design axis, not a preference.** Choose
relational when the data has strong cross-entity invariants that benefit from
joins and constraints enforced by the database itself. Choose document when
the natural unit of read/write is a single aggregate and forcing it into
normalized tables would mean joining on every read. Choose columnar/OLAP only
once analytical (scan-heavy, aggregate-heavy) queries would otherwise degrade
a transactional store — not from the start "in case we need analytics later"
(see Anti-patterns).

**Keys and constraints encode invariants, not just structure.** A foreign key
isn't bureaucracy — it's the database refusing to let an invariant be
violated. Every relationship should have an explicit ownership/cardinality
statement (one-to-many, many-to-many via a join structure, etc.), and every
field that must never be null, never be duplicate, or never reference a
missing row should say so in the schema, not just in application code.

More on the store-shape spectrum and per-technology security/auth/RLS
comparisons is in
[references/store-shape-comparison.md](references/store-shape-comparison.md).

## Decision framework

1. **What is the dominant access pattern?** Read-heavy on a single aggregate →
   lean document. Write-heavy with strong cross-entity invariants → lean
   relational. Scan/aggregate-heavy analytical queries at volume → lean
   columnar, but usually as a *second* store alongside an OLTP primary, not a
   replacement (see references).
2. **How strict does consistency need to be?** Multi-record invariants that
   must never be violated (double-booking, balance never negative) favor a
   relational store's transactional guarantees. Per-document consistency is
   often enough for MongoDB's document model.
3. **Is normalization actually buying anything here?** Normalize to remove
   real duplication/anomaly risk; denormalize deliberately where the read
   pattern is aggregate-shaped and joins would be pure overhead — but state
   which one you're doing and why, don't drift into inconsistent partial
   normalization.
4. **Would a second, specialized store solve a problem the primary store
   can't?** Don't add ClickHouse "for analytics" until analytical queries are
   actually degrading the OLTP store; don't add a document store alongside a
   relational one without a specific aggregate that justifies it.

## Workflow

1. Confirm requirements and access patterns are in hand (hand off to
   requirements-engineering if not).
2. Enumerate entities and their relationships; state cardinality explicitly.
3. Choose the store shape using the decision framework, citing the
   decision-matrix comparison where it applies.
4. Specify constraints that protect real invariants (keys, uniqueness,
   required fields, referential integrity).
5. Note where the schema is deliberately denormalized, and why.
6. Hand off implementation specifics to the matching technology skill
   (PostgreSQL/MySQL/MongoDB/etc.) and ORM mapping to
   [orm-integration](../orm-integration/SKILL.md).

## Engineering rules

- State cardinality and ownership for every relationship explicitly.
- Encode real invariants as constraints, not just as application-level checks.
- Don't claim a comparative performance advantage between stores that the
  research doesn't actually support — cite what's documented, flag what isn't.
- Justify denormalization by the access pattern, not by convenience.
- Add a second specialized store only once a specific, current need justifies it.

## Trade-offs

Normalization reduces duplication/anomaly risk but costs join complexity at
read time; denormalization speeds reads but risks update anomalies and
duplicated invariant-enforcement. Relational stores give strong
cross-row guarantees at the cost of schema rigidity; document stores give
schema flexibility at the cost of weaker cross-document guarantees. Neither
side is free — pick deliberately per §Decision framework.

## Anti-patterns

- **Adding a second specialized store "for later"** — a columnar OLAP store
  or a document store bolted on before there's an actual query pattern that
  needs it. This is the domain's overengineering trap.
- **Forcing a document-shaped access pattern into rigid third-normal-form
  tables**, producing a join on every read for data that's always read together.
- **Excessive cross-collection `$lookup` in a document store** — the
  research explicitly calls this out as a signal the data should be
  embedded/denormalized instead [Source: technology-decision-matrix.md §2].
- **Implicit relationships** — a "foreign key" that exists only in
  application logic, never enforced by the database.
- **Claiming an unresearched performance comparison** between store engines as if it were documented fact.

## Security

Row-level security support differs meaningfully by store: PostgreSQL has
native `ENABLE ROW LEVEL SECURITY` + `CREATE POLICY`, failing closed with no
policy defined; MongoDB's RBAC is documented but **not on by default** on
self-managed deployments; ClickHouse's Row Policies are one of five RBAC
entity types [Source: technology-decision-matrix.md §2]. Where the model
needs row-level tenant isolation, this choice materially affects which store
can enforce it natively vs. needing application-level enforcement. Deep
threat-modeling is owned by
[security-engineering](../../core/taxonomy/skill-catalog.md); this skill
only ensures the model has a place for the requirement.

## Performance

The store-shape choice is itself the biggest performance lever available at
design time — a mismatched shape (e.g. deep joins on a document store, or
point-queries at scale on ClickHouse, which the research notes is
inefficient by design [Source: technology-decision-matrix.md §2]) cannot be
fully fixed by indexing later. Query/index tuning depth is owned by
database-operations.

## Testing

Note a real, researched gap: PostgreSQL, MySQL, and (for application code
specifically) ClickHouse all have an **explicit documented absence of
official application-level testing guidance** — each delegates this to ORMs/
tooling or, for ClickHouse, documents testing ClickHouse itself rather than
app code against it [Source: technology-decision-matrix.md §2, "Application-test
methodology" row]. Don't assume official first-party testing guidance exists
for a schema design against these stores; MongoDB is the exception, with a
documented lightweight replica-set-for-testing topology and an official local
Docker image. Deep test-strategy method is owned by
[testing-strategy](../../core/taxonomy/skill-catalog.md).

## Failure handling

- If access patterns are unstated, ask rather than guessing a shape from the entities alone.
- If requirements are too thin, request them or hand off to requirements-engineering.

## Escalation

- A store-shape decision that's expensive to reverse in a live system (the
  primary datastore for something already in production) is presented with
  trade-offs for explicit confirmation before being treated as decided.

## Outputs & verification

- **Outputs:** an entity/relationship design with explicit keys and
  constraints, and a store-shape recommendation with recorded trade-offs.
- **Verify:** every relationship states cardinality/ownership; the chosen
  shape is justified against the actual access pattern; real invariants are
  encoded as constraints.

## References

- [references/store-shape-comparison.md](references/store-shape-comparison.md) — Tier-2 comparison table.
- [research/knowledge-maps/technology-decision-matrix.md](../../research/knowledge-maps/technology-decision-matrix.md)
- [research/knowledge-maps/concept-knowledge-map.md](../../research/knowledge-maps/concept-knowledge-map.md)
