# Sass — Breaking Changes (Tier-2 detail)

Loaded on demand from [`SKILL.md`](../SKILL.md) §Knowledge. All entries below
are version-specific claims (rule VA-2); tag any assertion drawn from this
file with the version it applies to.

[Source: https://sass-lang.com/documentation/breaking-changes/] The official
Breaking Changes index lists 25+ dated entries. Most recent entries retrieved
(version = first Dart Sass release to deprecate/warn):

| Change | First version to warn |
|---|---|
| Adjacent compound selectors | 1.100.0 |
| Additional plain CSS function names | 1.98.0 |
| Legacy `if()` function | 1.95.0 |
| Private variables in `with` | 1.92.0 |
| Misplaced rest arguments | 1.91.0 |
| `type()` function | 1.86.0 |
| `@import` | 1.80.0 |
| Legacy JS API | 1.79.0 |
| Color API deprecations | 1.79.0 |
| Color functions | 1.79.0 |
| `meta.feature-exists()` function | 1.78.0 |
| Mixed declarations with nested rules | 1.77.7 |
| Functions/Mixins beginning with `--` | 1.76.0 |
| `abs()` with percentage units | 1.65.0 |
| `null` alpha channel in `SassColor()` | 1.64.3 |
| Default export loading in JS | 1.63.0 |
| Duplicate variable flags | 1.62.0 |

Older entries from 1.0.0–1.55.0 (selectors, operators, CSS custom-property
syntax) are also listed on the official page but were not individually
re-fetched during the research pass behind this skill — consult
https://sass-lang.com/documentation/breaking-changes/ directly for those.

[Source: https://sass-lang.com/documentation/breaking-changes/import/]
`@import` deprecation detail: warnings began in 1.80.0; full removal
(treating `@import` as plain CSS only) is targeted for Dart Sass 3.0.0,
"which will not release sooner than two years after version 1.80.0"
[VERSION-SENSITIVE, forward-looking commitment, not yet in effect as of
1.104.0].

## Recent point-release behavioral changes

[Source: https://github.com/sass/dart-sass/releases] Not part of the
Breaking Changes index but documented as behavior changes in specific
releases:

- **1.104.0** — Colors now convert the special values `NaN` and negative
  zero, as well as infinity and negative infinity for polar-hue channels, to
  `0` per the CSS spec; negative zero now serializes as `-0` in calculation
  contexts.
- **1.103.0** — Color-space conversions now "preserve 'analogous sets' of
  missing channels during conversions, per the CSS spec," changing output
  for some conversions that previously zero-filled missing channels.
- **1.101.0** — Fixed how the Node package importer resolves import-only
  file variants; release notes flag this as a potential behavior break for
  code relying on the old resolution order.

## Why this matters

None of these are reasons to avoid upgrading Dart Sass — it is the only
actively maintained implementation (see `SKILL.md` §Anti-patterns) and ships
roughly every 1–4 weeks. The purpose of this table is to let the skill (or
the engineer using it) check, before asserting a specific Sass behavior,
whether that behavior is version-gated — per rule VA-2, an untagged
version-specific claim fails review.
