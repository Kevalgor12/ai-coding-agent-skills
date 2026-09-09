<!-- ILLUSTRATIVE EXAMPLE — Tier-2 reference file. Demonstrates that deep,
     bulky material lives here (loaded on demand) rather than in the SKILL.md
     body, per context-efficiency rules CE-2/CE-3. Content is abbreviated and
     representative; not authored library content. Every real claim would carry
     a source marker resolvable to skill.yaml.source_references. -->

# PostgreSQL — Indexing & MVCC (Tier-2 reference)

This file is loaded **only when the skill body links to it**, keeping the
always-on and on-activation tiers small.

## Index-type selection (decision table)

| Access pattern | Index type | Notes |
|---|---|---|
| Equality / range on scalar columns | B-tree | Default; covers `=`, `<`, `>`, `BETWEEN`, `ORDER BY`. [src: indexes] |
| Full-text search (`tsvector`) | GIN | Pair with `tsvector`; the standard in-DB FTS index. [src: fts] |
| `jsonb` containment / arrays | GIN | For `@>`, `?`, array membership. [src: indexes] |
| Geometric / nearest-neighbor | GiST | Also range/exclusion constraints. [src: indexes] |
| Very large, naturally-ordered tables | BRIN | Tiny index, block-range summaries; append-mostly data. [src: indexes] |

## Isolation levels (summary)

| Level | Prevents | Cost |
|---|---|---|
| Read Committed (default) | dirty reads | cheapest; non-repeatable reads possible |
| Repeatable Read | non-repeatable reads, most phantoms (snapshot) | serialization failures to retry |
| Serializable | all anomalies (SSI) | most retries; strongest guarantee |

Choose the weakest level that is correct for the transaction's invariants; retry
serialization failures rather than escalating the level blindly. [src: mvcc]

## MVCC & bloat

Readers see a snapshot; updates create new row versions and leave dead tuples.
Autovacuum reclaims them; long-open or idle-in-transaction sessions hold the
xmin horizon back and cause bloat. Keep transactions short. [src: mvcc]

## Row-level security (recipe shape)

```sql
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON orders
  USING (tenant_id = current_setting('app.tenant_id')::uuid);
```

RLS enforces access at the database regardless of the query source — a
defense-in-depth complement to application authorization, not a replacement.
[src: rls]
