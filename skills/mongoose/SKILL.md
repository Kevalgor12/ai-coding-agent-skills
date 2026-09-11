---
name: Mongoose
description: >-
  Mongoose-specific Schema/Model/Document design, middleware hooks,
  discriminators, change tracking, and type casting on MongoDB. Use when the
  stack uses Mongoose (mongoose npm package, Schema/Model/Document code,
  mongoose.connect()). Not for other ODMs/ORMs (orm-integration), generic
  MongoDB use with no Mongoose layer, or non-Mongoose-specific migration
  mechanics (data-migration).
spec_version: "1.0"
---

## Purpose & scope

Apply Mongoose correctly and version-appropriately as MongoDB's ODM:
Schema/Model/Document design, middleware/hooks, discriminators, change
tracking, and type casting. This skill specializes
[orm-integration](../orm-integration/SKILL.md) — the cross-ORM N+1 mitigation
table, the general transaction-handling method, and the top-level
CVE-2026-42334 summary live there and are not repeated here. It also
specializes [data-migration](../data-migration/SKILL.md) for Mongoose's
schema-less-but-still-evolving-document reality: MongoDB itself enforces no
schema, so "migration" for Mongoose means evolving the *Mongoose Schema* and
backfilling documents that predate it, not an ALTER TABLE.

## When to use / When not to use

**Use** when the `mongoose` package is a dependency, code defines a Mongoose
`Schema`/`Model` or calls `mongoose.connect()`, or the task names a
Mongoose-specific feature (middleware, discriminators, populate,
`sanitizeFilter`, `.lean()`). **Do not use** for a different ODM/ORM or the
raw MongoDB driver with no Mongoose layer (route to orm-integration or a
MongoDB-driver skill), for an open ORM/ODM *selection* decision (route to
orm-integration), or for migration mechanics with nothing Mongoose-specific
in question (route to data-migration).

## Knowledge

**Schema → Model → Document is the whole mental model.** A `Schema` maps to a
collection and declares its `SchemaType`s (String, Number, Date, Buffer,
Boolean, Mixed, ObjectId, Array, Decimal128, Map, UUID, Double, Int32); a
`Model` is "a fancy constructor compiled from a Schema definition"; a
`Document` is one instance of a Model, one-to-one with a stored MongoDB
document [Source: https://mongoosejs.com/docs/guide.html;
https://mongoosejs.com/docs/models.html; https://mongoosejs.com/docs/documents.html].
Subdocuments (embedded documents, single or arrays) have their own
schemas/validation but only persist via their parent's `save()`
[Source: https://mongoosejs.com/docs/subdocs.html].

**Registration order is a hard rule, not a style preference.** All
`schema.methods`, `schema.statics`, `schema.virtual()`, indexes, and
middleware must be attached to the Schema *before* `mongoose.model()` is
called — "the `.model()` function makes a copy of `schema`," and "calling
`pre()` or `post()` after compiling a model does not work in Mongoose in
general" [Source: https://mongoosejs.com/docs/models.html;
https://mongoosejs.com/docs/middleware.html]. Instance methods/statics/virtual
getters/setters/middleware must also never be arrow functions, since arrow
functions don't rebind `this` to the document/query/model
[Source: https://mongoosejs.com/docs/faq.html; https://mongoosejs.com/docs/guide.html].

**Middleware (pre/post hooks) run at document, query, aggregate, or
model-level for async operations** [Source:
https://mongoosejs.com/docs/middleware.html]. The pre-hook calling
convention is a version boundary: in Mongoose 9+, pre middleware no longer
receives a `next()` callback at all — hooks must be async
functions/promises; legacy `isAsync`-style hooks (`next` + `done`) are
unsupported [Source: https://mongoosejs.com/docs/migrating_to_9.html].
`[Version-sensitive: applies to mongoose >=9.0.0; ≤8.x hooks used the `next()`
callback style.]`

**Discriminators give schema inheritance on a shared collection.** Multiple
models with overlapping schemas share one underlying MongoDB collection,
distinguished by a discriminator key (default `__t`), via
`Model.discriminator(name, schema, key?)` [Source:
https://mongoosejs.com/docs/discriminators.html]. This is the right tool when
several document "types" genuinely share most fields and need to be queried
together — not a default for every schema variation (see Decision framework).

**Change tracking is why Documents aren't POJOs.** Documents carry internal
state (`$__`, modified-paths bookkeeping) for change detection; `delete`, spread
syntax, and `Object.keys()` don't behave as they would on a plain object, and
nested schema paths are pre-initialized as empty `{}` objects specifically
"as a performance optimization for change detection"
[Source: https://mongoosejs.com/docs/documents.html;
https://mongoosejs.com/docs/faq.html]. Consequence: mutating a `Date` (or
other object-valued) path in place — `doc.date.setMonth(1)` — is invisible to
change tracking unless you call `doc.markModified('date')` or reassign the
whole value [Source: https://mongoosejs.com/docs/faq.html].

**Type casting is automatic on Documents, not on aggregation results.**
Mongoose casts values to their declared `SchemaType` on document
construction/queries, but aggregation pipeline results are *not* hydrated
into Documents and are *not* auto-cast — a `$match` on a `Date` field needs a
manually cast `Date`, not a string [Source:
https://mongoosejs.com/docs/queries.html]. `ObjectId` casting is also looser
than expected: "any 12-character string is a valid ObjectId" per Mongoose's
default check, so validating for a real 24-character hex ObjectId requires an
explicit regex (`/^[a-f0-9]{24}$/`) [Source: https://mongoosejs.com/docs/faq.html].

Full `mongoose.set()` configuration option reference, the complete 8.x→9.x
breaking-change list, and debugging error signatures are in
[references/mongoose-reference.md](references/mongoose-reference.md).

## Decision framework

1. **How strict should the schema be?** `strict` (default `true`) rejects
   schema-undeclared fields on save; `strict: false` persists them;
   `strict: 'throw'` throws on them. `strictQuery` (default `false`)
   controls the same behavior specifically for *query filters*, separately
   from document writes [Source: https://mongoosejs.com/docs/api/mongoose.html].
   Default (`strict: true`, `strictQuery: false`) is the right starting point
   for most schemas — it's data-integrity protection against
   accidentally-persisted stray fields (e.g. from a request body) without
   also silently dropping legitimate query filters. Loosen `strict` only for
   a genuinely dynamic/freeform collection, not as a default.
2. **Is this logic a middleware/hook, or application code?** A pre/post hook
   is the right place for behavior that must *always* happen whenever a
   document is saved/removed/queried regardless of caller — e.g. a computed
   field derived purely from the document's own fields, cascading cleanup of
   a document's own subdocuments, or audit-logging that shouldn't depend on
   every call site remembering to do it. Application/service-layer code is
   the right place when the logic needs context beyond the single document
   (calling another service, orchestrating multiple models, anything that
   should be visible/testable independent of the save path) — burying
   multi-model orchestration inside a hook makes control flow hard to trace
   and hard to test in isolation. Default to the simplest option: if a single
   caller needs the behavior once, it doesn't need to be a hook.
3. **`.populate()` or an aggregation `$lookup`?** `.populate()` (with
   `select` to project only needed fields) is the default for straightforward
   reference-following — it's simpler to read and maintain. Reach for
   `Model.aggregate()` with `$lookup` instead when the read genuinely needs
   cross-document filtering/grouping/computation that populate can't express
   — populate cannot filter *parent* documents by a property on the
   *populated child* document, and sorting on a nested/array populated
   property is documented as "a known, difficult-to-fix issue"
   [Source: https://mongoosejs.com/docs/populate.html]. Don't reach for
   aggregation by default "for performance" without a concrete case populate
   can't handle — it trades readability and Document hydration (aggregation
   results aren't cast/hydrated, see Knowledge) for a single round-trip.
4. **Do you actually need a transaction, or is a single-document atomic
   write enough?** MongoDB single-document writes are already atomic;
   reach for `session.withTransaction()` (preferred over manual
   start/commit/abort — it retries transient errors automatically
   [Source: https://mongoosejs.com/docs/transactions.html]) only for
   genuinely multi-document atomicity, and remember transactions require a
   replica set or sharded cluster, not a standalone `mongod`
   [Source: https://mongoosejs.com/docs/change-streams.html].

## Workflow

1. Confirm the pinned Mongoose version (8.x vs. 9.x materially changes
   middleware signatures, `updatePipeline`'s default, and CVE exposure —
   see Security).
2. Design the Schema — SchemaTypes, `strict`/`strictQuery`, indexes,
   `timestamps` — with all methods/statics/virtuals/middleware/plugins
   attached before `mongoose.model()` is called.
3. Apply the Decision framework for middleware-vs-app-code and
   populate-vs-aggregation on each read/write path.
4. If the task touches security-sensitive input, verify `sanitizeFilter`
   status and Mongoose patch version (see Security) rather than assuming
   the flag alone is sufficient.
5. For schema changes on documents that already exist, hand off to
   [data-migration](../data-migration/SKILL.md)'s expand/contract method —
   add the new field/shape alongside the old, backfill, then stop reading
   the old shape once nothing depends on it; MongoDB's schema-less storage
   means old documents keep the old shape until backfilled, so a Mongoose
   Schema change alone does not touch existing data.

## Engineering rules

- Register all methods/statics/virtuals/indexes/middleware/plugins on the
  Schema before calling `mongoose.model()` — post-compilation registration is
  documented as not working [Source: https://mongoosejs.com/docs/models.html].
- Never use arrow functions for schema methods, statics, virtual
  getters/setters, or middleware — `this` won't bind to the
  document/query/model [Source: https://mongoosejs.com/docs/faq.html].
- Never call `.save()` in parallel on the same Document instance — throws
  `ParallelSaveError` [Source: https://mongoosejs.com/docs/faq.html].
- Reassign or `doc.markModified(path)` an in-place-mutated object-valued
  path (`Date`, nested object) — change tracking otherwise misses it
  [Source: https://mongoosejs.com/docs/faq.html].
- Don't treat `unique: true` as a validation guarantee — it only builds an
  index; call `await Model.init()` before relying on uniqueness in tests to
  ensure the index exists first [Source: https://mongoosejs.com/docs/faq.html].
- Reuse a `Query` only via `.clone()` — awaiting/executing the same Query
  object twice throws [Source: https://mongoosejs.com/docs/faq.html].
- Don't save a Document whose array was only partially loaded (via
  `$elemMatch` projection or a limited/skipped populate) — risks
  `DivergentArrayError`; reload the full array or use atomic positional
  updates instead [Source: https://mongoosejs.com/docs/faq.html].

## Trade-offs

Strict schemas (`strict: true`, the default) cost a small amount of
flexibility for genuinely dynamic data, in exchange for catching
accidentally-persisted stray fields — worth it for almost every schema.
Middleware centralizes always-true document-level behavior at the cost of
making control flow harder to trace across the codebase; the more a hook
does beyond the document's own fields, the more that cost outweighs the
convenience. `.lean()` trades getters/virtuals/change-tracking/`.save()` for
materially lower overhead on read-heavy paths — a real win, but only where
those Document features genuinely aren't needed
[Source: https://mongoosejs.com/docs/tutorials/lean.html].

## Anti-patterns

- **Assuming `sanitizeFilter` alone makes user-supplied query filters safe.**
  It is disabled by default, and even enabled, it had a real bypass
  (CVE-2026-42334, see Security) — verify the patched version, don't just
  flip the flag and stop thinking about it.
- **Registering middleware or schema methods after `mongoose.model()` has
  already been called** — documented as not working, not merely
  discouraged [Source: https://mongoosejs.com/docs/models.html].
- **Reaching for a discriminator for every schema variation** — the
  domain's over-engineering trap: discriminators are for genuine shared-collection
  polymorphism, not a default way to avoid writing two similar schemas.
- **Building an aggregation pipeline "for performance" when `.populate()`
  with `select` already answers the query** — adds complexity and gives up
  Document hydration for no real gain when populate wasn't actually the
  bottleneck.
- **Relying on `unique: true` as a correctness guarantee under load** without
  confirming the index actually exists (`Model.init()`) — a race window lets
  duplicates through as a driver-level error, not a clean `ValidationError`
  [Source: https://mongoosejs.com/docs/faq.html].
- **Using Jest's fake timers with Mongoose** — stubs `setTimeout`/`setInterval`
  and breaks the MongoDB driver's connection monitoring
  [Source: https://mongoosejs.com/docs/faq.html]. See Testing.

## Security

`sanitizeFilter` wraps any nested query-filter key starting with `$` in
`$eq` to neutralize operator injection from user input (e.g. `{ pwd: { $ne:
null } }` → `{ pwd: { $eq: { $ne: null } } }`); it is a `mongoose.set()`
global or per-query option, and it is **disabled by default**
[Source: https://mongoosejs.com/docs/api/mongoose.html].

**CVE-2026-42334** (High, CVSS 7.5): `sanitizeFilter` failed to recursively
sanitize inside the `$nor` operator — because `$nor` takes an array value and
arrays didn't trigger the "has-dollar-keys" check, an attacker-controlled
`$nor` clause could smuggle unsanitized operators (`$ne`, `$gt`, `$regex`,
etc.) past `sanitizeFilter` even with it enabled, risking authentication
bypass and unauthorized data access. Apps that whitelist/validate input
fields explicitly (e.g. `Model.findOne({ user: req.body.user, pwd:
req.body.pwd })`) were not affected [Source:
https://github.com/Automattic/mongoose/security/advisories/GHSA-wpg9-53fq-2r8h].
`[Version-sensitive: affects <6.13.9, 7.0.0-7.8.8, 8.0.0-8.22.0, 9.0.0-9.1.5;
patched in ^6.13.9, ^7.8.9, ^8.22.1, ^9.1.6.]` A follow-up hardening fix
shipped in 8.24.3 (2026-08-10) — "Applied sanitizeFilter to countDocuments
and cursor operations" — but the official advisory text for exactly what
those operations were missing beyond `$nor` was not located.
**Unresolved: whether the 8.24.3 countDocuments/cursor fix corresponds to
its own disclosed CVE, or is a proactive hardening change** [Source: raw
CHANGELOG at https://raw.githubusercontent.com/Automattic/mongoose/master/CHANGELOG.md].

Schema `strict` mode (default `true`) rejects schema-undeclared fields on
save, which is a relevant mass-assignment-adjacent protection when a schema
is populated directly from a request body, though the docs frame it as a
data-integrity feature rather than an explicit security control
[Source: https://mongoosejs.com/docs/guide.html] — `[Inference, not confirmed
as an explicit security statement in docs]`. `mongoose.set('debug', true)`
logs every collection call with its arguments; disable it in production —
community guidance suggests this can leak sensitive data into logs, but this
specific caution is not itself stated on an official Mongoose security page
`[Inference, not confirmed in docs]` [Source: https://mongoosejs.com/docs/faq.html].
Mongoose also documents integration with MongoDB Client-Side Field Level
Encryption (CSFLE) for encrypting specific fields client-side; the
schema-level API for declaring encrypted fields was not extracted in this
research pass — **Unresolved**, verify current syntax against
[Source: https://mongoosejs.com/docs/field-level-encryption.html] before use.
Deep threat modeling beyond Mongoose-specific mechanics is owned by
[security-engineering](../../core/taxonomy/skill-catalog.md).

## Performance

`save()` on an existing Document sends an `updateOne()` containing only the
*modified paths*, not the full document — a partial-update efficiency
property of Mongoose's change tracking, not a full-document rewrite
[Source: https://mongoosejs.com/docs/documents.html]. `.lean()` skips
Document hydration for read-heavy paths that don't need change
tracking/getters/virtuals/`.save()`, returning plain JS objects — Documents
"are much heavier than vanilla JavaScript objects" due to internal state
[Source: https://mongoosejs.com/docs/tutorials/lean.html]. For cross-document
reads, `.populate()` with `select` to limit projected fields is the baseline
mitigation for over-fetching (full cross-ORM N+1 pattern owned by
[orm-integration](../orm-integration/SKILL.md)); avoid `perDocumentLimit`
specifically, since it issues one query per parent document rather than a
single batched query [Source: https://mongoosejs.com/docs/populate.html].
`autoIndex` (default enabled) calls `createIndex()` for every declared index
on connect — disable it in production and build indexes out-of-band, since
index builds on a large collection can degrade performance
[Source: https://mongoosejs.com/docs/connections.html]. Tune
`maxPoolSize`/`minPoolSize` (default `maxPoolSize` 100) to expected
concurrency [Source: https://mongoosejs.com/docs/connections.html]. Recent
point releases target this directly:
`[Version-sensitive]` 9.9.0 (2026-07-30) improved `toObject` performance and
`insertMany` efficiency; 9.9.3 (2026-08-17) cached projection metadata;
9.7.1 (2026-06-17) improved save performance
[Source: raw CHANGELOG at https://raw.githubusercontent.com/Automattic/mongoose/master/CHANGELOG.md].

## Testing

Mongoose's own docs **explicitly discourage Jest**: "We strongly recommend
using a different testing framework, like Mocha"
[Source: https://mongoosejs.com/docs/jest.html]. **If Jest must be used**,
the documented requirements are specific and easy to miss:
`testEnvironment: 'node'` is required (Jest's default `jsdom` environment
stubs `setTimeout()` in ways that silently break Mongoose); never use Jest's
fake/mock timers (`jest.useFakeTimers()`) since they stub
`setTimeout`/`setInterval` and break the MongoDB driver's connection
monitoring — if genuinely unavoidable, import Mongoose *before* calling
`useFakeTimers()`, though the docs note this "may still cause issues"; avoid
Jest's `globalSetup` for opening the DB connection, since it runs in an
isolated environment inaccessible to test files; set `resetModules: false`
to avoid multiple Mongoose module instances breaking `instanceof` checks; and
run with `SUPPRESS_JEST_WARNINGS=1` to suppress Jest's own warnings
[Source: https://mongoosejs.com/docs/jest.html]. For features requiring a
replica set (change streams, transactions), use `mongodb-memory-server` or
`run-rs` locally [Source: https://mongoosejs.com/docs/change-streams.html].
For uniqueness testing, call `await Model.init()` first so unique indexes
exist before asserting duplicate-key behavior
[Source: https://mongoosejs.com/docs/faq.html]. **Unresolved:** no canonical
official end-to-end testing-strategy page (fixtures, factories, rollback
patterns) was found beyond the Jest-caveats page and scattered FAQ notes.
Deep test-strategy method beyond Mongoose specifics is owned by
[testing-strategy](../../core/taxonomy/skill-catalog.md).

## Failure handling

- If the pinned Mongoose version isn't known, ask for it or state the
  version range (`>=8.0 <=9.x`) the guidance assumes — `sanitizeFilter`'s CVE
  exposure, `updatePipeline`'s default, and the pre-middleware `next()`
  signature all differ materially between 8.x and 9.x.
- If shell is unavailable, degrade to advisory schema/config/code output and
  say that index builds, a live-connection check, or a migration were not run.

## Escalation

- A schema change to a field/shape used by documents that already exist is a
  migration, not a pure code change — hand off to
  [data-migration](../data-migration/SKILL.md) for the expand/contract
  sequence and destructive-step confirmation gate rather than treating a
  Schema edit as automatically applying to existing data.

## Outputs & verification

- **Outputs:** Schema/Model/Document code with correctly-ordered
  registration; `sanitizeFilter`/`strict` configuration and CVE-aware version
  guidance; a populate-vs-aggregation and middleware-vs-app-code analysis for
  the task at hand.
- **Verify:** methods/statics/virtuals/middleware are registered before
  `mongoose.model()`; any user-input-derived query filter is either
  whitelisted or backed by a patched (post-CVE-2026-42334) Mongoose version;
  every version-specific claim carries the Mongoose range it holds for.

## References

- [references/mongoose-reference.md](references/mongoose-reference.md) —
  Tier-2: full `mongoose.set()` config option table, complete 8.x→9.x
  breaking-change list, and FAQ debugging error signatures.
- [research/technologies/mongoose.md](../../research/technologies/mongoose.md)
- [research/knowledge-maps/technology-decision-matrix.md §1](../../research/knowledge-maps/technology-decision-matrix.md)
- [research/knowledge-maps/version-matrix.md](../../research/knowledge-maps/version-matrix.md)
- [orm-integration](../orm-integration/SKILL.md) — cross-ORM N+1 mitigation, transaction handling, ORM-selection framework
- [data-migration](../data-migration/SKILL.md) — expand/contract migration method
