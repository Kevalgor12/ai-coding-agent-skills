# core

Agent-agnostic foundations that every skill and adapter depends on. This is the
contract layer of the library — it does not contain any skill content itself.

Expected to eventually hold things like:

- The skill schema/spec (what fields a skill manifest must have, required
  metadata, versioning rules)
- Shared validation logic (e.g. "does this skill conform to the schema")
- Shared conventions/documentation (naming, structure, style guide for
  authoring a skill)
- Any common utility code that skills or adapters need and shouldn't
  duplicate

Nothing in this directory should be specific to one target agent (Claude
Code, Cursor, Codex, etc.) or one particular skill's subject matter. If it's
specific to an agent, it belongs in `adapters/`. If it's a skill's actual
content, it belongs in `skills/`.

Empty for now — no schema or validation logic has been defined yet.
