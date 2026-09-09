# Issue / status / changelog templates (Tier-2 reference)

Loaded only when [SKILL.md](../SKILL.md) links here. Templates, not rules —
adapt to the project's existing conventions when one exists (the same
detect-first discipline [git-conventions](../../../core/taxonomy/skill-catalog.md)
applies to commit style applies here to issue/changelog style).

## Issue draft template

```
## Goal
<what this achieves, in one or two sentences>

## Context
<why this is needed; link the originating discussion/requirement if any>

## Constraints
<anything that shapes the solution: performance, compatibility, deadline>

## Acceptance criteria
- <independently verifiable criterion>
- <independently verifiable criterion>

## Out of scope
<explicitly what this issue does NOT cover, to prevent scope creep>
```

Acceptance criteria here should reuse whatever
[requirements-engineering](../../requirements-engineering/SKILL.md) already
produced, if it ran earlier in the effort — don't re-derive them from scratch.

## Status summary template

```
**Done:** <what's shipped/verified>
**In progress:** <what's actively being worked>
**Blocked:** <what's stuck, and on what>
**Next:** <what's planned next>
```

Keep it to what changed since the last update, not a full re-narration of the
whole effort every time.

## Changelog entry template

```
- <type>: <what changed, from the user's/consumer's perspective>
```

Where `<type>` matches the project's existing changelog categorization if one
exists (e.g. Added / Changed / Fixed / Removed, or the Conventional-Commits-style
prefixes `git-conventions` would already be using for the underlying commits —
prefer consistency between the two rather than inventing a third taxonomy).

Write the entry from what actually shipped (check the diff/PR), not from the
original issue's ambition — a feature that shipped smaller than planned gets a
changelog entry describing the smaller, real thing.
