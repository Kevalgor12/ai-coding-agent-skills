# Runtime comparison notes (Tier-2 reference)

Loaded only when [SKILL.md](../SKILL.md) links here. This project's research
does **not** contain a direct, official, head-to-head comparison of Node.js
vs. Go vs. Python for backend service workloads (unlike the Fastify-vs-Express
and OpenAPI-vs-GraphQL comparisons, which do exist in
[technology-decision-matrix.md](../../../research/knowledge-maps/technology-decision-matrix.md)).
This file distills what each runtime's *own* research doc states about itself
— not a ranked comparison, since none is documented.

## Concurrency model

| Runtime | Model | Source |
|---|---|---|
| Node.js | Single-threaded event loop (libuv) + a worker thread pool for blocking work; non-blocking I/O is the default posture | `research/technologies/nodejs.md` |
| Go | Goroutines + channels; explicit multi-value `(value, error)` returns instead of exceptions | `research/technologies/go.md` |
| Python | Global Interpreter Lock (GIL) constrains true multi-threaded CPU parallelism; process-based parallelism (`multiprocessing`) is the traditional escape hatch; free-threaded (no-GIL) builds are experimental as of 3.13 and becoming officially supported as of 3.14 (PEP 703/779) | `research/knowledge-maps/version-matrix.md`, Python section |

## What each runtime's own docs emphasize

- **Node.js**: non-blocking I/O suits high-concurrency, I/O-bound workloads
  (many simultaneous connections doing relatively little CPU work each); a
  CPU-bound task blocks the single event loop unless explicitly offloaded to
  a worker thread.
- **Go**: goroutines are cheap enough to spawn per-request without a thread-pool
  abstraction; the explicit-error-return philosophy (vs. exceptions) is a
  deliberate design choice documented as encouraging error handling at the
  call site rather than propagating silently.
- **Python**: the GIL has historically meant CPU-bound multi-threading
  doesn't parallelize; free-threaded builds are the documented, actively
  evolving answer to this, but as of this research they are still
  new/opt-in, not yet the unqualified default — check the Python version
  actually in use before assuming free-threading is available.

## Using this without inventing a ranking

Do not present one runtime as generally "faster" or "better" than another —
the underlying research explicitly does not contain that comparison, unlike
the Fastify/Express and OpenAPI/GraphQL pairs which do. Base a runtime
recommendation on the team's actual constraints (existing expertise, workload
shape — I/O-bound vs. CPU-bound, deployment target) rather than an
unresearched performance claim.
