---
name: Code commenting
description: >-
  Write and review in-code comments. Use when writing or editing source code, or
  reviewing it for comment quality. Requires the "why" (constraints, invariants,
  workarounds); prevents step-narration, AI signatures, decorative bars, and
  comments that restate obvious code. Not for prose docs (use technical-documentation).
spec_version: "1.0"
---

<!-- ILLUSTRATIVE EXAMPLE: minimal valid SKILL.md body. Abbreviated; not the
     authored SK-CONV-002 skill. Shows only the required body sections for a
     generic engineering-convention skill. -->

## Purpose & scope

Write comments that carry information the code cannot state itself, and remove
comment noise. Covers in-code comments only — prose docs are a different skill.

## When to use / When not to use

**Use** when writing or substantially editing source, or reviewing code for
comment quality. **Do not use** for README/markdown/prose docs (that is
technical-documentation), or in a file whose established style deliberately uses
banner conventions — match the local norm instead.

## Engineering rules

- Comment the *why*: constraints, invariants, workarounds for a specific bug,
  and behavior that would surprise a reader.
- Do **not** add: phase/step narration (`// Step 1:`, `// now loop…`), AI/tool
  signatures or attribution inside code, decorative bars/separators, or comments
  that restate what the code already says plainly.
- Match the file's existing comment style and density.
- Prefer deleting a stale or redundant comment over rewording it.

## Anti-patterns

- **Over-commenting** — narrating every line; treat this as the domain's
  over-engineering trap (spec QR-4).
- Leaving a comment that will drift out of sync with the code it describes.

## Failure handling

- If the file's comment style is unclear, match the nearest sibling file rather
  than imposing a new convention.

## Outputs & verification

- **Output:** edited source (or review findings).
- **Verify:** no added comment merely restates adjacent code; no step-narration,
  AI-signature, or decorative comment was introduced.
