# Mongoose reference detail (Tier-2)

Loaded only when [SKILL.md](../SKILL.md) links here. Condensed from
[research/technologies/mongoose.md](../../../research/technologies/mongoose.md)
— consult that document for the full citation trail and additional
unresolved items not repeated here.

## Global configuration (`mongoose.set(key, value)`)

[Source: https://mongoosejs.com/docs/api/mongoose.html]

| Option | Default | Effect |
|---|---|---|
| `debug` | off | Logs every collection method call; accepts boolean, options object (`color`/`shell`/`timestamp`), a writable stream, or a custom `(collectionName, methodName, ...args) => {}` callback. Disable in production. |
| `strict` | `true` | Controls whether schema-undeclared fields may be saved (`false` \| `true` \| `'throw'`). |
| `strictQuery` | `false` | Same strictness concept, applied to query filters specifically (separate from document writes). |
| `autoIndex` | `true` | Automatic index builds on connect. Disable in production; build out-of-band instead. |
| `allowDiskUse` | — | Enables disk use for aggregation when `true`. |
| `maxTimeMS` | — | When set, attaches a server-side timeout to every query. |
| `sanitizeFilter` | disabled | Wraps `$`-prefixed keys in nested query objects with `$eq`. See SKILL.md Security for the CVE-2026-42334 caveat. |
| `selectPopulatedPaths` | enabled | Auto-selects populated fields. |
| `translateAliases` | disabled | Converts schema aliases to real paths before querying. |
| `runValidators` | disabled | Enables validators on `update`-family operations. |
| `updatePipeline` | disabled (Mongoose 9+) | Permits array/aggregation-pipeline update syntax. `[Version-sensitive: always-allowed in ≤8.x, opt-in from 9.0.0.]` |
| `toJSON` / `toObject` | `{ transform: true, flattenDecimals: true }` | Serialization control. |
| `overwriteModels` | disabled | When enabled, re-registering a model name overwrites instead of throwing. |
| `cloneSchemas` | — | — |
| `applyPluginsToChildSchemas` | enabled | — |
| `applyPluginsToDiscriminators` | disabled | — |

Per-schema options (`new Schema(defObj, options)`)
[Source: https://mongoosejs.com/docs/guide.html]: `_id` (auto ObjectId
assignment, disable-able per-subdocument), `timestamps` (adds
`createdAt`/`updatedAt`), `strict`, `autoIndex`, `minimize` (strips
empty-object fields on save, default enabled).

Connection-level options (`mongoose.connect()`/`createConnection()`)
[Source: https://mongoosejs.com/docs/connections.html]: `bufferCommands`
(queue pre-connection operations), `autoIndex`, `autoCreate`, `maxPoolSize`
(default 100), `minPoolSize`, `socketTimeoutMS` (default 0 = no timeout),
`serverSelectionTimeoutMS` (default 30s — governs both initial connect and
mid-operation retries), `heartbeatFrequencyMS` (docs advise not going below
1000ms), `user`/`pass`, `authSource`, `dbName`, `family` (force IPv4/IPv6),
`replicaSet`. `bufferTimeoutMS` controls how long buffered pre-connection
operations wait before timing out (documented default queues up to 10
seconds) [Source: https://mongoosejs.com/docs/faq.html].

## Migrating 8.x → 9.x — full breaking-change list

[Source: https://mongoosejs.com/docs/migrating_to_9.html] `[Version-sensitive: mongoose >=9.0.0]`

- **Middleware**: pre hooks no longer receive a `next()` callback at all —
  async functions/promises only. Legacy `isAsync`-style hooks (`next` +
  `done`) are unsupported; custom method/static hooks must be async
  (callback style no longer triggers hooks). `Document.prototype.updateOne`
  no longer accepts a callback.
- **Validation**: `Schema.prototype.doValidate()` returns a Promise instead
  of taking a callback.
- **Updates**: array/aggregation-pipeline update syntax disallowed by
  default unless `updatePipeline: true` is set. The `background` index
  option was removed (unsupported since MongoDB 4.2+). `new`/`returnOriginal`
  options are deprecated in favor of `returnDocument: 'after' | 'before'`.
- **Internals**: `caster`/`casterConstructor` removed, replaced by
  `embeddedSchemaType`/`Constructor`. `noListener` removed from `useDb()`.
  The third parameter to `Model()`/`Document()` constructors must be an
  options object — the legacy boolean `skipId` shortcut is removed.
  `skipOriginalStackTraces` removed. `promiseOrCallback` internal helper
  removed.
- **Types**: `isValidObjectId()` now returns `false` for numeric input;
  ObjectIds can no longer be constructed from numbers. UUID schema-typed
  fields now return `bson.UUID` instances (not strings) via getters. The
  `use$geoWithin` property (auto-converting `$geoWithin`→`$within`) was
  removed.
- **Environment**: Node.js **20.19.0** minimum.
- **TypeScript**: `FilterQuery` renamed to `QueryFilter`, now enforcing
  stricter typing (previously-permissive `any` resolution on mismatched
  operators/fields now errors). `create()`/`insertOne()` no longer accept
  generic type parameters. Document `.id` is now typed `string` (was `any`).
- **Subdocuments**: subdocument `deleteOne()` hooks now only fire when the
  subdocument is actually removed (after a parent `save()` or explicit
  `deleteOne()`), not unconditionally.

Earlier major-version headlines (not deeply verified beyond the headline
item; see [Source] for each):
- 7.x→8.x removed `findOneAndRemove()` (use `findOneAndDelete()`)
  [Source: https://mongoosejs.com/docs/migrating_to_8.html].
- 6.x→7.x removed `remove()` on documents/models (use
  `deleteOne()`/`deleteMany()`) [Source: https://mongoosejs.com/docs/migrating_to_7.html].
- 5.x→6.x: a Mongoose-reserved word used as a schema path name now warns,
  suppressible via `suppressReservedKeysWarning`
  [Source: https://mongoosejs.com/docs/migrating_to_6.html].

**Unresolved** (per the source research): full breaking-change lists for the
6→7 and 7→8 jumps were not deep-fetched — only headline items are captured
above.

## Currently-flagged deprecation

[Source: https://mongoosejs.com/docs/deprecations.html]
`Document.prototype.validateSync()` is deprecated as of Mongoose 9.9.5 and
slated for removal in Mongoose 10 (not yet released), because it bypasses
validate middleware and async validators — use
`Document.prototype.validate()` instead. `[Version-sensitive, forward-looking]`

## Debugging — recognizable error signatures

[Source: https://mongoosejs.com/docs/faq.html] The FAQ page is Mongoose's
de facto debugging reference:

| Error / symptom | Cause | Fix |
|---|---|---|
| `connect ECONNREFUSED ::1:27017` | Node 18+ prefers IPv6 for `localhost` | Connect to `127.0.0.1` explicitly, or enable IPv6 on the MongoDB server |
| `"Operation timed out after 10000 ms"` | No active connection when a query was issued | Ensure `mongoose.connect()` completed first |
| `mongodb+srv://` DNS resolution failures | Especially on Windows or ISP-intercepted DNS | `dns.setServers([...])` at app entry |
| `"x.$__y is not a function"` | Multiple/conflicting Mongoose package versions installed | `npm list | grep mongoose` |
| `ParallelSaveError` | Concurrent `.save()` calls on the same document instance | Serialize saves on one document |
| `DivergentArrayError` | Saving a document whose array field was only partially loaded | Reload the full array, or use atomic positional-operator updates |

For date-mutation-not-persisting bugs, `doc.markModified(path)` is the
documented diagnostic/fix tool.

## Deployment specifics (serverless)

[Source: https://mongoosejs.com/docs/lambda.html] AWS Lambda: cache the
connection (or the connection Promise) in module/global scope for reuse
across warm invocations; set `context.callbackWaitsForEmptyEventLoop =
false` so the cached connection can actually be reused on the next
invocation; bound `serverSelectionTimeoutMS` (docs' example: 5000ms) to
avoid indefinite hangs if the DB is unreachable.

[Source: https://mongoosejs.com/docs/nextjs.html] Next.js: `mongoose.connect()`
is a no-op when already connected, so it's safe to call defensively in every
API route/Server Component. Guard model registration with
`mongoose.models.X || mongoose.model('X', schema)` for hot-reload safety.
Next.js **Edge Runtime is not supported** — it lacks the Node.js `net` API
the MongoDB driver requires. For ESM/top-level-await errors under Next.js:
`esmExternals: "loose"`, `serverComponentsExternalPackages: ["mongoose"]`,
and enabling webpack `topLevelAwait` in `next.config.js`.

[Source: https://mongoosejs.com/docs/connections.html] Prefer `127.0.0.1`
over `localhost` in connection strings, because Node.js 18+ resolves
`localhost` to IPv6 first by default, which can break local-only deployments
not listening on `::1`.
