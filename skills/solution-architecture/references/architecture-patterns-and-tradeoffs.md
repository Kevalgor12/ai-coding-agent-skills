# Architecture patterns & trade-offs (Tier-2 reference)

Loaded only when [SKILL.md](../SKILL.md) links here. General architecture-style
trade-offs, complementing (not duplicating) the technology-specific comparisons
in [technology-decision-matrix.md](../../../research/knowledge-maps/technology-decision-matrix.md).
This file is style-of-system guidance; that file is which-technology guidance.

## System decomposition styles

| Style | Fits when | Costs |
|---|---|---|
| **Monolith / modular monolith** | One team or a few tightly-coordinated teams; no independent-scaling need per module; fastest path to shipping and to cross-module refactors. | Whole-system deploys; a hot module can force scaling the whole app. |
| **Service-oriented (a few coarse services)** | Real seams exist (independent scaling, independent deploy cadence, a genuine team boundary) but full microservice granularity isn't justified. | Cross-service calls need real error handling; some duplicated logic is often the right trade for decoupling. |
| **Microservices (fine-grained)** | Many independent teams, genuinely independent scaling/failure domains, mature deployment/observability tooling already in place. | Distributed-systems tax: network calls where function calls used to be, eventual consistency, much harder local reasoning, real operational overhead. |
| **Serverless / functions** | Spiky or unpredictable load, minimal ops appetite, workloads that fit short-lived execution. | Cold starts, vendor execution-model lock-in, harder to reason about end-to-end latency and local dev parity. |

Default to the least distributed shape that satisfies the stated
requirements; move right only when a specific requirement demands it, not on
general principle.

## Communication styles

| Style | Fits when | Costs |
|---|---|---|
| **Synchronous request/response (REST/GraphQL)** | The caller needs the result now; simpler tracing/debugging. | Caller blocks on callee's availability/latency; cascading-failure risk if not isolated. |
| **Asynchronous / event-driven** | Producers and consumers can be decoupled in time; resilience to a consumer being temporarily down matters more than immediate consistency. | Harder to trace/debug (a lost or delayed event isn't obvious); eventual consistency has to be designed for, not assumed away. *(Note: this project's research found no dedicated message-broker technology beyond Redis pub/sub — treat broker choice as outside current library grounding and verify independently.)* |
| **Realtime/bidirectional (WebSocket/Socket.IO/WebRTC)** | The interaction is inherently live (chat, presence, collaborative editing, media). | Connection lifecycle/reconnection and horizontal-scaling (sticky sessions or a shared pub/sub) become first-class concerns — see [realtime-communication](../../../core/taxonomy/skill-catalog.md). |

## Data-layer shape

| Shape | Fits when | Costs |
|---|---|---|
| **Single relational store** | Data is relational, ACID matters, the team knows SQL well. | Scaling writes horizontally is harder than for some NoSQL shapes. |
| **Polyglot persistence (SQL + cache + search + …)** | Different access patterns genuinely need different engines (e.g. relational source of truth + Redis cache + a dedicated search engine). | Each additional store is another thing to operate, back up, and keep consistent with the others — justify each one against a real access pattern, not by default. |
| **OLTP + separate OLAP** | Analytical queries would otherwise degrade the transactional store. | A second system to keep in sync (ETL/CDC); only worth it once analytics load is actually a problem. |

## Failure-mode checklist (architectural level)

Not exhaustive, but the recurring ones worth checking against any proposed shape:

- **Single point of failure** — does any one component's outage take down the
  whole system, and is that acceptable given the availability requirement?
- **Cascading failure** — can one slow/failing dependency exhaust callers'
  resources (connection pools, threads) and take them down too? (Timeouts,
  circuit breakers, bulkheads are the usual answers — flag the need, defer the
  implementation to the relevant domain skill.)
- **Split-brain / data divergence** — for anything replicated or eventually
  consistent, what happens when replicas disagree?
- **Retry storms** — do failures trigger retries that make the failure worse?
- **Silent data loss** — is there a path where a write can be acknowledged and then lost?

Identifying these at the architecture stage is cheap; discovering them in
production is not.
