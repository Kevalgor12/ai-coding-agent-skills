# Express 4.x → 5.x migration reference (Tier-2)

Deep material for `SK-TECH-express`. Loaded only when a 4.x→5.x migration is
actually in scope — not part of the Tier-1 `SKILL.md` body (context-efficiency
rule CE-3). Every claim here is already stated in
`research/technologies/express.md` §11/§13 and cited to the same
`expressjs.com` pages listed in `skill.yaml.source_references`.

## Route-path syntax table

[Source: https://expressjs.com/en/guide/routing.html, https://expressjs.com/en/guide/migrating-5.html]

| Pattern | Express 4.x | Express 5.x |
|---|---|---|
| Trailing wildcard | `/files/*` | `/files/*splat` or `/files/{*splat}` (wildcards **must** be named) |
| Optional segment | `/:file.:ext?` | `/:file{.:ext}` (brace syntax) |
| Optional leading slash + param | (ad hoc) | `{/:id}` |
| Multiple alternatives | `/[a|b]` (character-class-style) | `['/a', '/b']` (an array of path strings) |
| Reserved characters | fewer chars needed escaping | `()[]?+!` must be escaped explicitly |

**Practical effect:** any 4.x route using `/*`, a bare optional param
(`:ext?`), or `[a|b]`-style alternation will either fail to register or match
differently under 5.x. Search the codebase for these patterns before
upgrading; don't assume "it still parses" is the same as "it still matches
the same requests."

## Non-route-syntax breaking changes (4.x → 5.x)

[Source: https://expressjs.com/en/guide/migrating-5.html]

- **Removed:** `app.del()` (use `app.delete()`); `app.param(fn)`/`router.param(fn)` single-callback form; pluralized-only `req.accepts*` naming (`req.acceptsCharset()` → `req.acceptsCharsets()`, etc.); `req.param(name)` (use `req.params`/`req.body`/`req.query` explicitly); `res.json(obj, status)`/`res.jsonp(obj, status)` two-arg forms (use `.status().json()`); `res.send(body, status)`/`res.send(status)` (use `.status().send()` or `res.sendStatus()`); `res.redirect('back')`/`res.location('back')` magic string; `res.sendfile()` lowercase (use `res.sendFile()`); `express.static.mime` (use the `mime-types` package); array argument to `router.param(name, fn)`.
- **Changed defaults:** `express.urlencoded({ extended })` now defaults to `false` (was `true`); `req.body` is `undefined` when unparsed (was `{}`); `req.host` now includes the port (4.x stripped it); `req.query` is a read-only getter with default parser `"simple"` (was `"extended"`, and was writable).
- **Changed behavior:** `req.params` has a null prototype; wildcard captures are arrays; unmatched optional params are omitted rather than `undefined`; `res.clearCookie()` ignores `maxAge`/`expires` options passed to it; `res.status()` only accepts integers 100–999 and throws otherwise; `res.vary()` throws (was a warning) if the field argument is missing; `app.listen()`'s callback now receives an error argument (e.g. for `EADDRINUSE`); `app.router` is a real, lazily-created property again (it existed in 3.x, was removed in 4.x, and returns in 5.x with different underlying mechanics).
- **Non-breaking improvements:** `res.render()` is now always asynchronous across all view engines (no more synchronous-engine fast path); Brotli (`Content-Encoding: br`) decompression is supported by `express.json/urlencoded/text/raw`; MIME type table updates from an updated `mime-db` (notably `.js` served as `text/javascript`, not `application/javascript`); the router debug-log namespace moved from `express:router` to `router`/`router:*`; rejected/thrown errors from `async` handlers are automatically forwarded to the error handler (no more `.catch(next)` boilerplate).

## Automated migration tooling

[Source: https://expressjs.com/en/guide/migrating-5.html] Official codemods:
`npx codemod@latest @expressjs/v5-migration-recipe` (runs the full recipe), or
individually: `@expressjs/route-del-to-delete`,
`@expressjs/pluralize-method-names`, `@expressjs/explicit-request-params`,
`@expressjs/status-send-order`, `@expressjs/redirect-arg-order`,
`@expressjs/back-redirect-deprecated`, `@expressjs/camelcase-sendfile`,
`@expressjs/sendfile-options`, `@expressjs/static-dotfiles`,
`@expressjs/static-mime`.

**Recommended sequence:** run the full codemod recipe first, then manually
search for route strings matching the patterns in the table above (codemods
handle API renames well but route-path rewriting still needs a human read),
then re-run the test suite against both the up- and down-level behavior of
any endpoint that depended on `req.body` defaulting to `{}` or
`extended: true` parsing.
