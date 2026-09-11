# Mongoose (MongoDB Object Modeling for Node.js)

Research date: 2026-09-09
Primary official source: https://mongoosejs.com/ (docs hosted at `mongoosejs.com/docs/`)
Secondary official sources: GitHub org repo `https://github.com/Automattic/mongoose` (source, CHANGELOG, security advisories)

[Source: https://mongoosejs.com/] The canonical documentation host is still `mongoosejs.com` as of this research date — no host migration was observed. Version-specific doc snapshots are served under versioned paths (e.g. `mongoosejs.com/docs/6.x/docs/...`), with the unversioned `mongoosejs.com/docs/...` paths always reflecting the current major version (9.x at research time).

---

## 1. Core Concepts

[Source: https://mongoosejs.com/] Mongoose is described as "Elegant MongoDB object modeling for Node.js," providing built-in type casting, validation, query building, and business logic hooks on top of the MongoDB Node.js driver.

[Source: https://mongoosejs.com/docs/guide.html] "Everything in Mongoose starts with a Schema." A Schema maps to a MongoDB collection and defines the shape/structure of the documents within that collection, including permitted **SchemaTypes**: String, Number, Date, Buffer, Boolean, Mixed, ObjectId, Array, Decimal128, Map, UUID, Double, and Int32.

[Source: https://mongoosejs.com/docs/models.html] A **Model** is "a fancy constructor compiled from a Schema definition." Models are the interface used to create, query, update, and delete documents in a specific MongoDB collection. Calling `mongoose.model('Tank', schema)` compiles the schema and, by default, maps to a lowercased/pluralized collection name (`Tank` → `tanks`).

[Source: https://mongoosejs.com/docs/documents.html] A **Document** is an instance of a Model, representing a one-to-one mapping to a document stored in MongoDB. Documents extend Mongoose's `Document` class and provide change tracking, validation, middleware, and persistence (`save()`) on top of the raw data.

[Source: https://mongoosejs.com/docs/subdocs.html] **Subdocuments** are documents embedded in other documents (single nested subdocuments or arrays of subdocuments); they have their own schemas/validation but are not saved independently — they persist only when their top-level parent is saved.

[Source: https://mongoosejs.com/docs/populate.html] **Population** is Mongoose's mechanism for replacing a stored reference (`ObjectId`, etc.) with the actual referenced document(s) via a separate query — described as "Mongoose's alternative to MongoDB's `$lookup` operator."

[Source: https://mongoosejs.com/docs/middleware.html] **Middleware** (pre/post hooks) are schema-level functions that run during execution of asynchronous document, query, aggregate, or model-level operations.

[Source: https://mongoosejs.com/docs/discriminators.html] **Discriminators** provide schema inheritance: multiple models with overlapping schemas can share a single underlying MongoDB collection, distinguished by a discriminator key (default `__t`).

---

## 2. Architecture

[Source: https://mongoosejs.com/docs/connections.html] Mongoose sits as a layer on top of the official MongoDB Node.js driver. `mongoose.connect(uri, options)` establishes the default connection; `mongoose.createConnection(uri, options)` creates additional, independent Connection instances, each with its own connection pool and model registry — the docs recommend exporting **schemas** (not compiled models) to support multi-connection architectures, since models are scoped to the connection that compiled them.

[Source: https://mongoosejs.com/docs/connections.html] Underlying connection responsibilities — pooling, DNS resolution, authentication, and TLS/SSL — are delegated to the MongoDB driver; Mongoose configures and exposes these via options like `maxPoolSize`, `minPoolSize`, `serverSelectionTimeoutMS`, and `heartbeatFrequencyMS`.

[Source: https://mongoosejs.com/docs/connections.html] Two connection-pool architecture patterns are documented for multi-tenant apps: (1) a single pool with `Connection.prototype.useDb()` to switch logical databases per request (simpler, less scalable), and (2) multiple pools/connections held in a per-tenant map (more scalable, requires care to avoid exceeding MongoDB's connection limits).

[Source: https://mongoosejs.com/docs/queries.html] Query builder methods (`find`, `findOne`, etc.) return a **Query** object, which is "thenable" but not a true Promise — it does not resolve until `.exec()`/`.then()`/`await` triggers execution, and it can only be executed once (re-`await`ing throws "Query was already executed"; `.clone()` is required to safely re-run it).

[Source: https://mongoosejs.com/docs/documents.html] Documents are not plain JavaScript objects: the `delete` operator, spread syntax, and `Object.keys()` do not behave as they would on a POJO because Documents carry internal state for change tracking (`$__`, modified-paths bookkeeping, etc.). `toObject()`/`toJSON()` convert a Document into a plain object.

[Source: https://mongoosejs.com/docs/api.html] The primary API surface areas are: `Mongoose` (singleton entry point), `Schema`, `SchemaType`, `Connection`, `Model`, `Document`, `Query`, `Aggregate`, and `VirtualType`.

---

## 3. APIs

[Source: https://mongoosejs.com/docs/models.html] Document creation/read/update/delete surface:
- Construction: `new Model(obj)` + `doc.save()`; `Model.create(obj)`; `Model.insertMany([...])`.
- Reads: `Model.find()`, `Model.findOne()`, `Model.findById()`, chainable `.where()`.
- Updates: `Model.updateOne()`, `Model.updateMany()`, `Model.findOneAndUpdate()`, `Model.findByIdAndUpdate()`.
- Deletes: `Model.deleteOne()`, `Model.deleteMany()`, `Model.findOneAndDelete()`, `Model.findByIdAndDelete()`.
- Real-time: `Model.watch()` opens a change stream (requires replica set/sharded cluster — see §16).
- Views: `Model.createCollection()` with `viewOn`/`pipeline` options creates a read-only MongoDB View.

[Source: https://mongoosejs.com/docs/queries.html] Cursors/streaming: `Model.find().cursor()` with `cursor.next()`, or `for await (const doc of Model.find())` async iteration; default cursor timeout is 10 minutes, overridable with `addCursorFlag('noCursorTimeout', true)`.

[Source: https://mongoosejs.com/docs/guide.html] Schema-attached API surfaces: `schema.methods` (instance methods — must not be arrow functions, since they need `this` bound to the document), `schema.statics`/`schema.static()` (Model-level functions, same arrow-function restriction), `schema.query` (chainable query-helper methods), `schema.virtual()` (computed, non-persisted properties), and `schema.plugin()` (schema mixins).

[Source: https://mongoosejs.com/docs/populate.html] `Query.prototype.populate(path | { path, select, match, populate, perDocumentLimit })` — supports deep/nested population, virtual populate (`ref` + `localField` + `foreignField` on a virtual), dynamic refs via `refPath` or a function `ref`, and cross-database populate by passing a Model class instead of a string. `doc.populated(path)` checks population state; `doc.depopulate(path)` reverts it.

[Source: https://mongoosejs.com/docs/transactions.html] Transaction API: `mongoose.startSession()` / `connection.startSession()`; `session.withTransaction(fn)` (recommended — handles commit/abort/transient-error retry automatically); `Connection#transaction()` (Mongoose wrapper with document change-tracking integration); low-level `session.startTransaction()` / `session.commitTransaction()` / `session.abortTransaction()`. `doc.$session()` accesses/sets a document's associated session.

[Source: https://mongoosejs.com/docs/api/mongoose.html] `mongoose.set(key, value)` configures global options (full list in §4). `mongoose.isObjectIdOrHexString()` and other static Mongoose-namespace helpers are also documented on this reference page.

[Source: https://mongoosejs.com/docs/discriminators.html] `Model.discriminator(name, schema, key?)` creates a discriminator model sharing the base model's collection.

---

## 4. Configuration

[Source: https://mongoosejs.com/docs/api/mongoose.html] Global configuration is set via `mongoose.set(optionName, value)`. Documented options include:
- `debug` — logs MongoDB collection method calls; accepts boolean, an options object (`color`/`shell`/`timestamp`), a writable stream, or a custom logging callback.
- `strict` — default `true`; controls whether schema-undeclared fields may be saved (`false` | `true` | `'throw'`).
- `strictQuery` — default `false`; controls strict-mode behavior specifically for query filters (`false` | `true` | `'throw'`).
- `autoIndex` — default `true` (enabled); disable globally to stop automatic index builds on connect.
- `allowDiskUse` — enables disk use for aggregation by default when `true`.
- `maxTimeMS` — when set, attaches a server-side timeout to every query.
- `sanitizeFilter` — default disabled; wraps `$`-prefixed keys in nested query objects with `$eq` to mitigate query-selector injection (see §7 for a documented bypass/CVE).
- `selectPopulatedPaths` — default enabled; auto-selects populated fields.
- `translateAliases` — default disabled; converts schema aliases to real paths before querying.
- `runValidators` — default disabled; enables validators on `update`-family operations.
- `updatePipeline` — default disabled in Mongoose 9 (see §13); permits array/aggregation-pipeline update syntax.
- `toJSON` / `toObject` — default `{ transform: true, flattenDecimals: true }`; control serialization.
- `overwriteModels` — default disabled; when enabled, re-registering a model name overwrites instead of throwing.
- `cloneSchemas`, `applyPluginsToChildSchemas` (default enabled), `applyPluginsToDiscriminators` (default disabled).

[Source: https://mongoosejs.com/docs/guide.html] Per-schema options (second argument to `new Schema(defObj, options)`) include `_id` (auto ObjectId assignment, can be disabled per-subdocument), `timestamps` (adds `createdAt`/`updatedAt`), `strict`, `autoIndex`, and `minimize` (strips empty-object fields on save, default enabled).

[Source: https://mongoosejs.com/docs/connections.html] Connection-level options passed to `mongoose.connect()`/`createConnection()`: `bufferCommands` (queue operations issued before the connection opens), `autoIndex`, `autoCreate`, `maxPoolSize` (default 100), `minPoolSize`, `socketTimeoutMS` (default 0 = no timeout), `serverSelectionTimeoutMS` (default 30s — governs both the initial connect and subsequent operation retries), `heartbeatFrequencyMS` (docs advise not going below 1000ms), `user`/`pass`, `authSource`, `dbName`, `family` (force IPv4/IPv6), and `replicaSet`.

[Source: https://mongoosejs.com/docs/faq.html] `bufferTimeoutMS` controls how long buffered (pre-connection) operations wait before timing out (documented default behavior queues for up to 10 seconds before the "Operation timed out" error).

---

## 5. Recommended Patterns

[Source: https://mongoosejs.com/docs/models.html] Define all schema methods, statics, virtuals, indexes, and middleware **before** calling `mongoose.model()` — "the `.model()` function makes a copy of `schema`," so changes to the schema object after compilation do not propagate to the compiled model.

[Source: https://mongoosejs.com/docs/middleware.html] Corollary: "Calling `pre()` or `post()` after compiling a model does **not** work in Mongoose in general" — hooks must be registered pre-compilation.

[Source: https://mongoosejs.com/docs/connections.html] For multi-connection apps, export Schemas rather than compiled Models so each connection can independently call `.model()` on the same schema definition.

[Source: https://mongoosejs.com/docs/nextjs.html] In serverless/hot-reload environments (Next.js specifically), guard model compilation with `mongoose.models.User || mongoose.model('User', UserSchema)` to avoid "Cannot overwrite model once compiled" errors, and rely on `mongoose.connect()` being a no-op when already connected rather than manually tracking connection state.

[Source: https://mongoosejs.com/docs/lambda.html] For AWS Lambda / serverless deployments, cache the connection (or connection promise) in a module-level/global variable and reuse it across invocations; set `context.callbackWaitsForEmptyEventLoop = false` so Lambda can keep the connection warm between invocations, and set a bounded `serverSelectionTimeoutMS` (docs' example uses 5000ms) so a failed connection attempt does not hang the function.

[Source: https://mongoosejs.com/docs/populate.html] Use `.select()` to project only needed fields on populated paths, and prefer denormalization over `perDocumentLimit`-based per-document population when performance matters, since `perDocumentLimit` issues a separate query per parent document.

[Source: https://mongoosejs.com/docs/tutorials/lean.html] For read-heavy, high-performance paths where you don't need change tracking, virtuals, getters, or `.save()`, use `.lean()` to skip document hydration and receive plain JS objects.

[Source: https://mongoosejs.com/docs/transactions.html] Prefer `session.withTransaction()` over manually orchestrating `startTransaction`/`commitTransaction`/`abortTransaction`, since it automatically retries on MongoDB transient transaction errors.

[Source: https://mongoosejs.com/docs/plugins.html] Package cross-cutting schema behavior (timestamps, soft-delete, autopopulate, etc.) as plugins (`schema.plugin(fn)` or global `mongoose.plugin(fn)`) rather than duplicating logic per schema; apply plugins before model compilation for the same reason middleware must be registered pre-compilation.

---

## 6. Anti-patterns

[Source: https://mongoosejs.com/docs/faq.html] Using arrow functions for schema methods, statics, virtual getters/setters, or middleware — arrow functions do not rebind `this`, so `this` will not refer to the document/query/model as Mongoose expects. (Confirmed independently in [Source: https://mongoosejs.com/docs/guide.html] for `methods`/`statics`.)

[Source: https://mongoosejs.com/docs/faq.html] Calling `.save()` in parallel on the same document instance — throws a `ParallelSaveError` due to conflicting validation/change state.

[Source: https://mongoosejs.com/docs/faq.html] Mutating a `Date` (or similar object-valued) path in place, e.g. `doc.date.setMonth(1)`, and expecting `save()` to persist it — Mongoose's change detection won't see the mutation unless you call `doc.markModified('date')` or reassign the whole value.

[Source: https://mongoosejs.com/docs/faq.html] Relying on `unique: true` as a validation guarantee — it only builds a MongoDB index; under race conditions before the index exists (or is fully built), duplicates can slip through and surface as a driver-level duplicate-key error rather than a Mongoose `ValidationError`. Calling `await Model.init()` ensures the index exists before relying on uniqueness in tests.

[Source: https://mongoosejs.com/docs/faq.html] Re-`await`ing or reusing the same `Query` object without `.clone()` — causes duplicate query execution.

[Source: https://mongoosejs.com/docs/faq.html] Saving a document whose array was partially loaded (e.g. via `$elemMatch` projection or a `populate()` with `limit`/`skip`) — risks a `DivergentArrayError`; the docs recommend reloading the full array or using atomic positional-operator updates instead.

[Source: https://mongoosejs.com/docs/queries.html] Treating aggregation pipeline results as hydrated, type-cast Mongoose documents — aggregation does not hydrate results into Documents and does not auto-cast types (e.g., dates in `$match` must be cast manually).

[Source: https://mongoosejs.com/docs/nextjs.html] Assuming Mongoose works in the Next.js Edge Runtime — it explicitly does not, because the Edge Runtime lacks the Node.js `net` API the MongoDB driver requires.

[Source: https://mongoosejs.com/docs/jest.html] Using Jest's fake timers (`jest.useFakeTimers()`) with Mongoose — stubbed `setTimeout`/`setInterval` break the MongoDB driver's connection monitoring and event-loop-dependent behavior; the docs go as far as to say they "strongly recommend using a different testing framework, like Mocha" for Mongoose apps generally.

---

## 7. Security

[Source: https://mongoosejs.com/docs/api/mongoose.html] `sanitizeFilter` (a `mongoose.set()` global option, or per-query) defends against **query-selector injection**: it wraps any nested object whose key starts with `$` in a `$eq`, so e.g. user-supplied `{ pwd: { $ne: null } }` becomes `{ pwd: { $eq: { $ne: null } } }`, neutralizing the operator injection. It is **disabled by default**.

[Source: https://github.com/Automattic/mongoose/security/advisories/GHSA-wpg9-53fq-2r8h] **CVE-2026-42334** (High severity, CVSS 7.5): the `sanitizeFilter` mechanism failed to recursively sanitize inside the `$nor` operator. Because `$nor` takes an array value, and arrays didn't trigger the "has-dollar-keys" sanitization check, an attacker-controlled `$nor` clause could smuggle unsanitized operators (`$ne`, `$gt`, `$regex`, etc.), allowing NoSQL injection even with `sanitizeFilter` enabled. Affected: mongoose `<6.13.9`, `7.0.0–7.8.8`, `8.0.0–8.22.0`, `9.0.0–9.1.5`. Patched in `^6.13.9`, `^7.8.9`, `^8.22.1`, `^9.1.6`. Potential impact: authentication bypass, unauthorized data access, data exfiltration for apps that rely on `sanitizeFilter` to neutralize raw user input passed into query filters (apps that validate/whitelist input fields, e.g. `Model.findOne({ user: req.body.user, pwd: req.body.pwd })`, were not affected). [Version-sensitive]
[Source: raw CHANGELOG at https://raw.githubusercontent.com/Automattic/mongoose/master/CHANGELOG.md] A related follow-up hardening fix shipped in 8.24.3 (2026-08-10): "Applied sanitizeFilter to countDocuments and cursor operations" — Unresolved: the official docs/advisory text describing exactly which operations were previously excluded from `sanitizeFilter` coverage (beyond `$nor`) was not directly located; this CHANGELOG line is the only evidence found and its full technical detail (e.g., whether this was itself tied to a CVE) could not be verified from an official page.

[Source: https://mongoosejs.com/docs/faq.html] Debug mode / logging: enabling `mongoose.set('debug', true)` logs all collection method calls and arguments; community-adjacent guidance surfaced in search (not itself from mongoosejs.com, so treated as inference) suggests this can leak sensitive data (credentials, PII) into logs if left on in production. [Inference, not confirmed in docs] — the mongoosejs.com pages fetched describe `debug`'s mechanics but did not explicitly state a security warning about leaking sensitive data; this caution is standard practice but not verified as an explicit official doc statement.

[Source: https://mongoosejs.com/docs/field-level-encryption.html] Mongoose documents integration with **MongoDB Client-Side Field Level Encryption (CSFLE)** — encrypting specific fields client-side before they reach the server. Details of configuration were not deeply extracted in this pass; page exists and is official. Unresolved: exact schema-level API for declaring encrypted fields was not captured — flagging for follow-up rather than guessing at syntax.

[Source: https://mongoosejs.com/docs/guide.html] Schema `strict` mode (default `true`) prevents arbitrary/unexpected fields from being persisted, which is a relevant mass-assignment-style protection when schemas are populated from request bodies — though the docs frame this as a data-integrity feature, not explicitly as a security control. [Inference, not confirmed in docs] for the security framing specifically.

---

## 8. Performance

[Source: https://mongoosejs.com/docs/tutorials/lean.html] `.lean()` skips document "hydration" (conversion of raw driver POJOs into full Mongoose Documents with internal change-tracking state), returning plain JavaScript objects. Documents "are much heavier than vanilla JavaScript objects" due to this internal state; lean is recommended for "high-performance, read-only cases," especially combined with cursors. Trade-off: getters and virtuals do not run under `.lean()` unless a plugin (e.g., `mongoose-lean-virtuals`) is used.

[Source: https://mongoosejs.com/docs/connections.html] `autoIndex` (default enabled) automatically calls `createIndex()` for every declared index on connect; the docs explicitly recommend disabling this in production ("avoid performance degradation") since index builds on a large production collection can be expensive, and instead building indexes out-of-band.

[Source: https://mongoosejs.com/docs/connections.html] `maxPoolSize`/`minPoolSize` tuning: increase `maxPoolSize` (default 100) for workloads with slow queries needing more concurrent sockets; increase `minPoolSize` to avoid cold-pool slowdowns after idle periods.

[Source: https://mongoosejs.com/docs/populate.html] Populate performance guidance: use `select` to limit fields returned by populated documents; avoid `perDocumentLimit` unless necessary, since it issues one query per parent document rather than a single batched query; consider denormalizing frequently-populated fields instead of populating on every read.

[Source: https://mongoosejs.com/docs/documents.html] `save()` on an existing document sends an `updateOne()` containing only the modified paths, not the full document — an efficiency property of Mongoose's change tracking.

[Source: raw CHANGELOG at https://raw.githubusercontent.com/Automattic/mongoose/master/CHANGELOG.md] Recent point releases specifically targeted performance: 9.9.0 (2026-07-30) "Enhanced toObject performance and improved insertMany efficiency"; 9.9.3 (2026-08-17) "Cached projection metadata"; 9.7.1 (2026-06-17) "Improved save performance." [Version-sensitive — these are 9.7.x/9.9.x-line optimizations, not present in earlier 9.x or 8.x releases per the changelog entries examined.]

[Source: https://mongoosejs.com/docs/faq.html] Nested schema paths are pre-initialized as empty objects `{}` "as a performance optimization for change detection" (these don't get persisted if empty, per `minimize`).

---

## 9. Testing

[Source: https://mongoosejs.com/docs/jest.html] Official guidance explicitly discourages Jest: "We strongly recommend using a different testing framework, like Mocha," for testing Mongoose applications.

[Source: https://mongoosejs.com/docs/jest.html] If Jest must be used: set `testEnvironment: 'node'` (the default `jsdom` environment stubs `setTimeout()` in ways that silently break Mongoose); do not use Jest's fake/mock timers (they stub `setTimeout`/`setInterval`, breaking driver connection monitoring) — if unavoidable, import Mongoose before calling `useFakeTimers()`, though the docs note this "may still cause issues"; avoid Jest's `globalSetup` for opening DB connections since it runs in an isolated environment inaccessible to test files; set `resetModules: false` to avoid multiple Mongoose module instances breaking `instanceof` checks; and run with `SUPPRESS_JEST_WARNINGS=1` to suppress Jest's own warnings.

[Source: https://mongoosejs.com/docs/change-streams.html] For local testing of features requiring a replica set (e.g., change streams, transactions), the docs recommend `mongodb-memory-server` or `run-rs` to spin up a local replica set; for production, MongoDB Atlas is recommended.

[Source: https://mongoosejs.com/docs/faq.html] For uniqueness testing specifically, call `await Model.init()` first to guarantee indexes (including unique indexes) are built before asserting duplicate-key behavior — otherwise a race condition can let a duplicate write through before the index exists.

Unresolved: the official docs do not appear to publish a dedicated end-to-end "how to unit/integration test a Mongoose-backed app" guide beyond the Jest caveats page and scattered FAQ notes — no canonical official testing-strategy page (fixtures, factories, transaction rollback between tests, etc.) was found on mongoosejs.com.

---

## 10. Deployment

[Source: https://mongoosejs.com/docs/lambda.html] AWS Lambda: cache the connection (or the connection Promise) in module/global scope so it can be reused across warm invocations; set `context.callbackWaitsForEmptyEventLoop = false` so Lambda doesn't wait for the event loop to drain before freezing the container, which allows the cached connection to actually be reused on the next invocation; set a bounded `serverSelectionTimeoutMS` (example: 5000ms) to avoid indefinite hangs if the DB is unreachable. Two documented patterns: a reusable `connect()` helper built on `mongoose.createConnection()`, or a global-singleton `mongoose.connect()` + `mongoose.model()`.

[Source: https://mongoosejs.com/docs/nextjs.html] Next.js / serverless in general: `mongoose.connect()` is a no-op when already connected, so it's safe to call it defensively in every API route or Server Component. Guard model registration with `mongoose.models.X || mongoose.model('X', schema)` for hot-reload safety. Next.js Edge Runtime is explicitly **not supported** (no Node `net` API). For ESM-related BSON/top-level-await errors under Next.js, the docs recommend `next.config.js` settings: `esmExternals: "loose"`, `serverComponentsExternalPackages: ["mongoose"]`, and enabling webpack `topLevelAwait`.

[Source: https://mongoosejs.com/docs/change-streams.html] Change streams and transactions require the target MongoDB deployment to be a replica set or sharded cluster — a standalone `mongod` will reject `$changeStream` with an explicit server error. MongoDB Atlas is the documented recommendation for production deployments needing this.

[Source: https://mongoosejs.com/docs/connections.html] Production connection guidance: disable `autoIndex` in production (see §8); tune `maxPoolSize`/`minPoolSize` to match expected concurrency; set `serverSelectionTimeoutMS` deliberately since it governs failover/retry behavior during elections in a replica set; prefer `127.0.0.1` over `localhost` because Node.js 18+ resolves `localhost` to IPv6 first by default, which can break local-only deployments not listening on `::1`.

---

## 11. Migration

[Source: https://mongoosejs.com/docs/migration.html] Mongoose publishes a dedicated Migration Guide index page linking version-specific guides for every major-version jump.

### Migrating 8.x → 9.x
[Source: https://mongoosejs.com/docs/migrating_to_9.html]
- **Middleware**: pre middleware hooks no longer receive a `next()` callback parameter at all — must use async functions/promises. Legacy `isAsync`-style hooks with both `next` and `done` are unsupported; custom method/static hooks must be async (callback style no longer triggers hooks). `Document.prototype.updateOne` no longer accepts a callback.
- **Validation**: `Schema.prototype.doValidate()` now returns a Promise instead of taking a callback.
- **Updates**: array/aggregation-pipeline update syntax is disallowed by default unless the `updatePipeline: true` option is set. The `background` index option was removed (unsupported since MongoDB 4.2+). `new`/`returnOriginal` options are deprecated in favor of `returnDocument: 'after' | 'before'`.
- **Internals**: `caster`/`casterConstructor` properties removed, replaced by `embeddedSchemaType`/`Constructor`. `noListener` option removed from `useDb()`. The third parameter to `Model()`/`Document()` constructors must be an options object — the legacy boolean `skipId` shortcut is removed. `skipOriginalStackTraces` removed (stack-trace storage eliminated). `promiseOrCallback` internal helper removed.
- **Types**: `isValidObjectId()` now returns `false` for numeric input; ObjectIds can no longer be constructed from numbers. UUID schema-typed fields now return `bson.UUID` instances (not strings) via getters. The `use$geoWithin` property (auto-converting `$geoWithin`→`$within`) was removed.
- **Environment**: Node.js **20.19.0** is the minimum supported version for Mongoose 9. [Version-sensitive]
- **TypeScript**: `FilterQuery` was renamed to `QueryFilter`, which now enforces stricter typing (previously-permissive `any` resolution on mismatched operators/fields now errors). `create()`/`insertOne()` no longer accept generic type parameters. Document `.id` is now typed as `string` (was `any`).
- **Subdocuments**: subdocument `deleteOne()` hooks now only fire when the subdocument is actually removed (after a parent `save()` or explicit `deleteOne()`), not unconditionally.

### Earlier major migrations (from search-result summaries; not deep-fetched this pass)
[Source: https://mongoosejs.com/docs/migrating_to_8.html] Migrating 7.x → 8.x includes removal of `findOneAndRemove()` (use `findOneAndDelete()`) among "several backwards-breaking changes." [Not deeply verified beyond this headline — Unresolved: full list of 7→8 breaking changes not fetched in this research pass.]

[Source: https://mongoosejs.com/docs/migrating_to_7.html] Migrating 6.x → 7.x includes removal of the `remove()` method on documents and models (use `deleteOne()`/`deleteMany()`) among "several backwards-breaking changes." [Not deeply verified beyond this headline — Unresolved: full list not fetched.]

[Source: https://mongoosejs.com/docs/migrating_to_6.html] Migrating 5.x → 6.x: using a Mongoose-reserved word as a schema path name now triggers a warning, suppressible via `suppressReservedKeysWarning`. [Headline only; Unresolved: full list not fetched.]

[Source: https://mongoosejs.com/docs/migrating_to_5.html] Migrating 4.x → 5.x: Mongoose required Node.js ≥ 4.0.0 and MongoDB ≥ 3.0.0 at that time. [Historical; superseded by later requirements.]

Mongoose's official docs do not present migration guidance *from* comparable alternative ODMs/ORMs (e.g., no official "migrating from Sequelize" or "migrating from Prisma" guide was found) — the documented migration content is exclusively version-to-version upgrade guidance within Mongoose itself.

---

## 12. Version Information

[Source: https://mongoosejs.com/] Current stable version at research time: **9.9.5**.

[Source: https://mongoosejs.com/docs/version-support.html] Documented major-version support status:
- **Mongoose 9** (current) — released 2025-11-21; latest observed patch 9.9.5 as of 2026-09-09 (page itself showed 9.9.3 at time of fetch — patch releases are frequent). Primary active-development branch.
- **Mongoose 8** (prior) — released 2023-10-31; latest observed 8.24.4; the version-support page states "support through February 1, 2026" while also noting it "continues receiving updates alongside version 9" — Unresolved: these two statements are in mild tension (an EOL date vs. "continues receiving updates"); the raw CHANGELOG shows 8.24.x patches still shipping as late as 2026-08-21, past the stated Feb 1, 2026 cutoff, so the practical EOL enforcement is unclear from docs alone.
- **Mongoose 7** (legacy) — released 2023-02-27; latest observed 7.8.12; "receives important fixes but no longer primary focus."
- **Mongoose 6** (limited maintenance) — released 2021-08-24; latest observed 6.13.11; security patches and requested bug fixes only; End of Life **2027-02-01**.
- **Mongoose 5** (end of life) — released 2018-01-17; EOL **2024-03-01**; no longer maintained.

[Source: https://mongoosejs.com/docs/version-support.html] The fetched page did not state an explicit release-cadence policy (e.g., "major every N months") — "Not documented / could not verify" for a formal cadence commitment. Empirically, per the raw CHANGELOG, patch/minor releases ship roughly weekly-to-biweekly on the active 9.x line, with parallel 8.x backport patches.

[Source: https://mongoosejs.com/docs/compatibility.html] MongoDB server compatibility matrix (Mongoose version ranges compatible with each MongoDB server major version):
| MongoDB Server | Compatible Mongoose |
|---|---|
| 8.x | `^8.7.0 \| ^9.0.0` |
| 7.x | `^7.4.0 \| ^8.0.0 \| ^9.0.0` |
| 6.x | `^7.0.0 \| ^8.0.0 \| ^9.0.0` |
| 5.x | `^6.0.0 \| ^7.0.0 \| ^8.0.0` |
| 4.4.x | `^6.0.0 \| ^7.0.0 \| ^8.0.0` |
| 4.2.x | `^6.0.0 \| ^7.0.0 \| ^8.0.0` |
| 4.0.x | `^6.0.0 \| ^7.0.0 \| ^8.0.0 <8.16.0` |
| 3.6.x | `^6.0.0 \| ^7.0.0 \| ^8.0.0 <8.8.0` |
Note: "Mongoose `^6.5.0` also works with MongoDB server 7.x" but with possible feature limitations per the docs. [Version-sensitive table — always check this live page for a specific pairing rather than trusting a cached copy.]

[Source: https://mongoosejs.com/docs/migrating_to_9.html] Node.js **20.19.0** minimum required for Mongoose 9. [Version-sensitive] Unresolved: minimum Node.js version specifically for Mongoose 8.x was not located in the fetched pages (only the 9.x requirement was explicit).

[Source: raw CHANGELOG at https://raw.githubusercontent.com/Automattic/mongoose/master/CHANGELOG.md] Underlying MongoDB Node.js driver version bumps are tracked in the changelog: 9.8.0 (2026-07-20) "upgraded MongoDB driver to 7.5"; 9.6.0 (2026-04-28) "upgraded MongoDB driver to 7.2." [Version-sensitive]

---

## 13. Breaking Changes

Covered in detail in §11 (Migration) for the 8→9 jump, the most recent major version boundary. Summary of the highest-impact breaking changes for teams upgrading to Mongoose 9, per [Source: https://mongoosejs.com/docs/migrating_to_9.html]:
1. Pre-middleware hooks lose their `next()` callback parameter entirely (async/Promise-only).
2. Node.js **20.19.0+** is now required.
3. Update pipelines (array syntax) are opt-in via `updatePipeline: true` rather than always allowed.
4. `new`/`returnOriginal` findAndModify-family options are deprecated for `returnDocument`.
5. TypeScript: `FilterQuery` → `QueryFilter` rename plus materially stricter type-checking of query filters (previously-silent type errors now fail to compile).
6. `isValidObjectId()` semantics changed for numeric input (now `false`).
7. UUID-typed fields return native `bson.UUID` objects instead of strings.

[Source: https://mongoosejs.com/docs/deprecations.html] Currently-flagged deprecation (not yet a breaking removal): `Document.prototype.validateSync()` is deprecated as of Mongoose 9.9.5 and slated for removal in Mongoose 10, because it bypasses validate middleware and async validators; use `Document.prototype.validate()` instead. [Version-sensitive — forward-looking to a not-yet-released Mongoose 10.] The fetched deprecations page appeared to show only this single entry; Unresolved: whether additional deprecations exist further down the page that weren't captured by the fetch tool's excerpt.

[Source: https://github.com/Automattic/mongoose/security/advisories/GHSA-wpg9-53fq-2r8h] CVE-2026-42334 constitutes a security-motivated breaking behavior change within patch releases (not a major version bump) — the `sanitizeFilter` `$nor` bypass was fixed in `6.13.9`, `7.8.9`, `8.22.1`, and `9.1.6` respectively; anyone depending on the old (vulnerable) `$nor` pass-through behavior would see stricter sanitization post-patch. See §7 for full detail.

---

## 14. Limitations

[Source: https://mongoosejs.com/docs/models.html] Change streams (`Model.watch()`) do **not** work against a standalone MongoDB instance — "change streams do not work unless you're connected to a MongoDB replica set" (or sharded cluster, per §16).

[Source: https://mongoosejs.com/docs/transactions.html] Running operations **in parallel inside a transaction is not supported** — the docs explicitly warn against `Promise.all()`/`Promise.race()` patterns within a transaction session. Nested transactions on the same session are also disallowed (throws "Transaction already in progress").

[Source: https://mongoosejs.com/docs/populate.html] Populate cannot filter *parent* documents by a property on the *populated* (child) document — there is no equivalent of a SQL join-then-filter-on-joined-column; the documented workaround is denormalization. Also: `limit` on a populate call applies globally across all matched parents by default, not per-parent (per-parent requires the slower `perDocumentLimit`, which issues one query per document). Sorting on a nested/array populated property (e.g. `arr.child`) is called out as "a known, difficult-to-fix issue."

[Source: https://mongoosejs.com/docs/nextjs.html] Mongoose does **not** currently support the Next.js Edge Runtime, since that runtime lacks the Node.js `net` module the MongoDB driver depends on.

[Source: https://mongoosejs.com/docs/tutorials/lean.html] `.lean()` query results do not run getters or virtuals, do not get defaults applied via the normal document-hydration path, and are not `Document` instances (no `.save()`, no change tracking) — this is a documented trade-off, not a bug.

[Source: https://mongoosejs.com/docs/faq.html] `ObjectId` validity checking is looser than many developers expect: "any 12-character string is a valid ObjectId" per Mongoose's default check, so validating for a specific 24-character hex representation requires an explicit regex (`/^[a-f0-9]{24}$/`) rather than relying on Mongoose's built-in ObjectId cast/validity check alone.

[Source: https://mongoosejs.com/docs/typescript.html] Mongoose's TypeScript support does not verify that your hand-written document interface actually matches your runtime schema — "Developer Responsibility": Mongoose "won't report errors if your interface contradicts schema constraints (like missing a required field)." This is a structural limitation of the schema-first + manually-declared-interface approach (as opposed to fully generated types).

---

## 15. Debugging

[Source: https://mongoosejs.com/docs/api/mongoose.html] `mongoose.set('debug', true)` logs every collection method call (with arguments) Mongoose sends to the underlying driver. `debug` also accepts an options object (`color`, `shell`, `timestamp` flags), a writable stream target, or a fully custom callback function `(collectionName, methodName, ...methodArgs) => {}` for custom log formatting/routing.

[Source: https://mongoosejs.com/docs/faq.html] The FAQ page functions as Mongoose's de facto debugging reference, documenting recognizable error signatures and their causes/fixes:
- `connect ECONNREFUSED ::1:27017` → Node 18+ preferring IPv6 for `localhost`; fix by connecting to `127.0.0.1` explicitly or enabling IPv6 on the MongoDB server.
- `"Operation timed out after 10000 ms"` → no active connection when a query was issued; ensure `mongoose.connect()` completed first.
- `mongodb+srv://` DNS resolution failures (especially on Windows or ISP-intercepted DNS) → explicitly set DNS servers via Node's `dns.setServers([...])` at app entry.
- `"x.$__y is not a function"` → multiple/conflicting Mongoose package versions installed; diagnose via `npm list | grep mongoose`.
- `ParallelSaveError` → concurrent `.save()` calls on the same document instance.
- `DivergentArrayError` → saving a document whose array field was only partially loaded.

[Source: https://mongoosejs.com/docs/faq.html] For date-mutation-not-persisting bugs, `doc.markModified(path)` is the documented diagnostic/fix tool to force Mongoose to recognize an in-place mutation as a change.

Unresolved: no dedicated official "Debugging Mongoose" guide/page distinct from the `debug` option (§4/§15) and the FAQ page was found — debugging guidance is distributed across the FAQ and the `mongoose.set('debug', ...)` API reference rather than centralized in one document.

---

## 16. Integration

[Source: https://mongoosejs.com/docs/nextjs.html] **Next.js**: officially documented integration guide covering connection caching (`mongoose.connect()` as an idempotent no-op), hot-reload-safe model registration, Edge Runtime non-support, and ESM/webpack config fixes (`esmExternals: "loose"`, `serverComponentsExternalPackages: ["mongoose"]`, `topLevelAwait`).

[Source: https://mongoosejs.com/docs/lambda.html] **AWS Lambda**: officially documented connection-reuse and `callbackWaitsForEmptyEventLoop` guidance (see §10).

[Source: https://mongoosejs.com/docs/change-streams.html] **MongoDB Change Streams**: officially documented `Model.watch()` integration, requiring a replica set or sharded cluster; for local dev, `mongodb-memory-server` or `run-rs`; for production, MongoDB Atlas. Supports both event-based (`.on('change', ...)`) and iterative/polling (`.next()` with `resumeAfter`) consumption patterns, the latter recommended for Lambda/serverless.

[Source: https://mongoosejs.com/docs/field-level-encryption.html] **MongoDB Client-Side Field Level Encryption (CSFLE)**: an official integration page exists; deep API details not fully captured in this pass (see §7 Unresolved note).

[Source: https://mongoosejs.com/docs/typescript.html] **TypeScript**: officially supported since Mongoose v5.11.0. [Version-sensitive] Provides `Schema<T>`, `model<T>()`, `HydratedDocument<T>` (full document w/ methods+virtuals, distinct from the raw document interface `T`), `InferSchemaType`-style inference patterns, and (as of the 9.x line per §11) a renamed/stricter `QueryFilter` type. The docs also mention striving for compatibility with community `@types/mongoose` typings and allow removing the bundled `index.d.ts` (with a recommendation to file a GitHub issue first) if it conflicts with custom typings.

[Source: https://mongoosejs.com/docs/plugins.html] **Plugin ecosystem**: Mongoose maintains a searchable plugin registry at `plugins.mongoosejs.io`; officially name-checked plugins include `mongoose-autopopulate`, `mongoose-lean-virtuals`, and `mongoose-cast-aggregation`. Community plugins are discoverable via the `mongoose` npm keyword.

[Source: https://mongoosejs.com/docs/jest.html] **Testing frameworks**: explicit official guidance for Jest compatibility caveats (§9); Mocha is the officially recommended alternative, though no dedicated "Mongoose + Mocha" walkthrough page was located in this pass (Unresolved).

[Source: https://mongoosejs.com/docs/version-support.html and https://mongoosejs.com/docs/compatibility.html] **MongoDB server versions**: officially documented compatibility matrix (§12) is itself a first-class "integration" contract between Mongoose and MongoDB server releases.

Not documented / could not verify: no official Mongoose documentation page for GraphQL integration, Prisma/other-ORM interop, Docker-specific deployment guidance, or CI-provider-specific setup was found in this research pass — these may exist as community content but were not located as official Mongoose docs.

---

## 17. Production Considerations

[Source: https://mongoosejs.com/docs/connections.html] Disable `autoIndex` in production to avoid index-build-triggered performance degradation on large collections; build/manage indexes out-of-band instead.

[Source: https://mongoosejs.com/docs/connections.html] Tune `maxPoolSize`/`minPoolSize` for expected concurrency; keep `heartbeatFrequencyMS` at 1000ms or above; set `serverSelectionTimeoutMS` deliberately since it governs both initial-connect retries and mid-operation retries during events like replica-set elections; handle both promise-rejection-style initial connection errors (`try { await mongoose.connect(...) } catch {}`) and post-connection async errors via the `mongoose.connection.on('error', ...)` event listener — these are two distinct error-handling surfaces that must both be covered.

[Source: https://mongoosejs.com/docs/faq.html / API debug docs] Disable `debug` logging in production (performance cost of generating extra log output, and — per general/inferred caution, see §7 — potential sensitive-data exposure); gate it behind an environment variable so it's development-only by construction.

[Source: https://mongoosejs.com/docs/lambda.html] In serverless/production-Lambda contexts, reuse cached connections across invocations and bound `serverSelectionTimeoutMS` so a DB outage fails fast instead of hanging function execution.

[Source: https://mongoosejs.com/docs/change-streams.html] Production real-time features (change streams) and transactions require a replica set or sharded cluster topology — a bare standalone `mongod` is not production-viable for apps depending on these features; MongoDB Atlas is the documented recommended production target.

[Source: https://mongoosejs.com/docs/api/mongoose.html] Consider enabling `sanitizeFilter` globally in production if user input ever reaches query filters, while being aware of the `$nor`-bypass CVE history (§7) and keeping Mongoose patched to at least `6.13.9`/`7.8.9`/`8.22.1`/`9.1.6` or later.

[Source: https://mongoosejs.com/docs/version-support.html] For production dependency planning: Mongoose 6.x reaches End of Life 2027-02-01; Mongoose 8.x's stated support window ("through February 1, 2026") is in documented tension with its continued patch releases observed in the changelog past that date (see §12 Unresolved) — teams should track the live version-support page rather than this snapshot when planning upgrade timing.

Not documented / could not verify: no official mongoosejs.com page dedicated specifically to "Production Checklist" or "Deploying to production" as a single consolidated guide was found — production guidance is distributed across the Connections guide, the Lambda/Next.js integration pages, the FAQ, and the API reference for `mongoose.set()`, as cited above, rather than centralized.

---

## Summary of Version-Sensitive Facts to Track

| Fact | Version / Range | Note |
|---|---|---|
| Node.js minimum | ≥ 20.19.0 | Required starting Mongoose 9 |
| Pre-middleware `next()` param | Removed | Mongoose 9+ (was present in ≤8.x) |
| `updatePipeline` default | Must opt in (`false` default) | Changed in Mongoose 9 |
| `FilterQuery` type name | Renamed to `QueryFilter` | Mongoose 9 TypeScript |
| UUID field return type | `bson.UUID` object (was string) | Mongoose 9+ |
| `isValidObjectId()` on numbers | Returns `false` | Changed in Mongoose 9 |
| `Document.prototype.validateSync()` | Deprecated, removal planned | Deprecated in 9.9.5, removal targeted for Mongoose 10 (not yet released) |
| `sanitizeFilter` `$nor` bypass (CVE-2026-42334) | Fixed in ^6.13.9, ^7.8.9, ^8.22.1, ^9.1.6 | Pre-patch versions vulnerable |
| TypeScript officially supported | Since v5.11.0 | — |
| Mongoose 8 support window | Stated "through Feb 1, 2026" but patches continued past that date per CHANGELOG | Unresolved tension, see §12 |
| Mongoose 6 EOL | 2027-02-01 | Security/requested-bug-fixes only until then |
| Mongoose 5 EOL | 2024-03-01 (already past) | No longer maintained |
| MongoDB driver bump to 7.5 | Mongoose 9.8.0 (2026-07-20) | — |
| MongoDB driver bump to 7.2 | Mongoose 9.6.0 (2026-04-28) | — |

## Unresolved Items (Full List)

1. Whether the Mongoose 8.x "support through February 1, 2026" statement is still operative, given patch releases (8.24.x) observed shipping through at least 2026-08-21 per the raw CHANGELOG.
2. Full technical detail behind the 8.24.3 CHANGELOG line "Applied sanitizeFilter to countDocuments and cursor operations" — whether this was its own disclosed CVE or a proactive hardening fix; no dedicated official advisory page was located for it.
3. Exact schema-level API syntax for MongoDB Client-Side Field Level Encryption integration (page confirmed to exist at `mongoosejs.com/docs/field-level-encryption.html`, but full API detail not extracted).
4. Complete breaking-change lists for the 6→7 and 7→8 major migrations (only headline items were captured via search-result summaries, not a full page fetch).
5. Minimum Node.js version specifically required for Mongoose 8.x (only the 9.x minimum of 20.19.0 was explicitly located).
6. Whether the `mongoose.set('debug', true)` option's sensitive-data-exposure risk is stated explicitly anywhere in official docs, or is only a general/inferred security caution.
7. Whether a canonical, single official "production checklist" or "testing strategy" page exists beyond the distributed guidance found across Connections/Lambda/Next.js/Jest/FAQ pages — none was found in this pass.
8. Whether additional entries exist on the deprecations page beyond the single `validateSync()` entry captured (the fetch tool's excerpt may not have captured the full page).
