# Individual skill quality review — Infrastructure/CI-CD + QA/Observability + Realtime (Layer 4)

Date: 2026-09-10. Step 28 of the master build plan: individual quality
review of every generated skill, this file covering the batch of 12
Layer-4 technology skills: `docker`, `github-actions`, `husky`,
`jest-vitest`, `playwright`, `opentelemetry`, `prometheus`, `grafana`,
`sentry`, `socketio`, `webrtc`, `websocket-api`.

Reviewed against `core/skill-specification/specification.md` (all VR/VA/CE/
SG/QR rules), `core/taxonomy/skill-catalog.md` (the Layer-4 shared template
and per-technology table row for each of the 12), `skills/code-commenting/
SKILL.md` (comment-quality yardstick), and each skill's own research doc
(`research/technologies/{docker,github-actions,husky,jest,vitest,
playwright,opentelemetry,prometheus,grafana,sentry,socketio,webrtc,
websocket-api}.md`) with spot-checked factual claims against the cited
source text. `opentelemetry`, `prometheus`, `grafana`, and `sentry` were
authored together in an earlier step and had already been through one
audit pass at that time; this is their first *individual*, 17-point review
— they were re-verified in full, not assumed correct.

All 12 `skill.yaml` files parsed as valid YAML both before and after the
edits below. Four narrow, mechanical defects were fixed during this review
(one type-shape defect, one field-type-mismatch bug — same root cause —
and five broken in-body markdown cross-references); everything else is
reported only, per the review's scope discipline.

## Summary

| Skill | Critical | High | Medium | Low |
|---|---|---|---|---|
| docker | 0 | 0 | 1 | 0 |
| github-actions | 1 (fixed) | 0 | 0 | 0 |
| husky | 0 | 0 | 1 | 0 |
| jest-vitest | 0 | 0 | 0 | 0 |
| playwright | 0 | 0 | 0 | 0 |
| opentelemetry | 0 | 0 | 0 | 0 |
| prometheus | 0 | 0 | 0 | 0 |
| grafana | 0 | 0 | 0 | 0 |
| sentry | 0 | 0 | 1 | 0 |
| socketio | 0 | 0 | 0 | 1 (fixed) |
| webrtc | 0 | 0 | 2 | 2 (fixed) |
| websocket-api | 0 | 0 | 0 | 2 (fixed) |
| **Total** | **1** | **0** | **5** | **5** |

No High-severity findings. Every skill passed: VR-1 (all required fields
present and well-typed, after the one github-actions fix below), VR-2
(`skill.yaml`/`SKILL.md` frontmatter `name`/`description` match exactly,
byte-for-byte, on all 12), VR-3 (`parents`/`related_skills`/`conflicts_with`
all resolve to real, existing skill IDs — every parent listed in
`skill-catalog.md`'s Layer-4 table was independently verified against the
target skill's actual `id:` field), VR-4 (`depends_on_skills: []` on all
12, trivially acyclic, and correctly reserved rather than conflated with
`parents` — the exact mistake the spec calls out as recurring elsewhere in
this project was not repeated here), VR-5 (`execution_tier`/
`required_capabilities` consistency, including `playwright`'s correct
Tier-C + `capability_fallbacks` shape — the only Tier-C skill in this
batch), VR-6 (activation/non-activation conditions disjoint on all 12,
confirmed programmatically), VR-7 (no duplicate activation trigger string
within this batch's 42 total triggers), CE-1 (all 12 descriptions ≤500
chars), CE-2 (all 12 `SKILL.md` bodies well under 500 lines — longest is
`opentelemetry` at 412), VA-1 (`covered_versions`+`reverify_triggers`
present on all 12), VA-4 (`last_verified: "2026-09-10"` on all 12), and
SG-1 (non-empty `source_references`, every entry resolving through the
correct `research/technologies/*.md` file with an ISO `retrieved` date).

**Technology accuracy was the standout strength of this batch.** Every
spot-checked factual claim — Docker's Engine API v1.56/v1.44 floor, GitHub
Actions' Node 20 removal date, Jest v27/v30 default changes, Vitest 5.0's
`clearMocks`/module-scope changes, Playwright's v1.60/62/63 boundaries
(including correctly flagging the macOS-13/Cookie-header version as
**unresolved** rather than stating it as settled, matching the research
doc's own honesty), OpenTelemetry's per-language/per-signal stability
matrix, Prometheus's v2.55→v3.0 TSDB-compatibility boundary, Grafana's
v11.0.0 legacy-alerting removal and v13.0.0 breaking changes, Sentry's v9
Metrics-API removal (explicitly cited, matching this project's own prior
finding that it is "the strongest evidence Sentry is error/trace/session
monitoring, not a metrics platform"), Socket.IO's v2→v3/v3→v4 boundaries,
WebRTC's Plan-B→Unified-Plan Chrome M65–M96 timeline, and WebSocket API's
RFC 6455 masking/close-code/Node-client-only facts — traced cleanly back
to the cited research doc with no invented API surface found anywhere in
the batch. The `opentelemetry`/`prometheus`/`grafana`/`sentry` four-way
"composition not competition" finding from the original audit still holds:
`conflicts_with: []` on all four, and each one's "When not to use" section
correctly routes to the other three rather than re-explaining their
scope. The `jest-vitest` merge is genuinely coherent (not two bolted-together
halves): it treats the choose-one decision as one skill with one shared
snapshot/mocking-API narrative and a single decision framework, exactly as
the taxonomy's merge rationale calls for. The `socketio`/`webrtc`/
`websocket-api` three-way boundary shows no duplicated transport-concern
re-explanation — each owns a structurally distinct mechanism (Socket.IO's
own Engine.IO layer, WebRTC's ICE/STUN/TURN/SDP, raw RFC 6455 framing) and
cross-references the other two instead of restating them.

---

## docker

**Medium — stale "not yet authored" parenthetical about a parent skill
that now exists.** `skill.yaml` line 9 (`# containerization;
security-engineering (not yet authored)`), line 23-24 (in `scope:`, "deep
cross-cutting threat modeling is owned by security-engineering (SK-QA-002,
not yet authored in this library)"), line 44 (in `non_activation_
conditions:`, "route to security-engineering, SK-QA-002, not yet
authored"), and `SKILL.md` lines 26 and 209 (same phrasing) all assert
that `SK-QA-002` / `security-engineering` has not been authored yet.
It has: `skills/security-engineering/skill.yaml` exists with `id:
SK-QA-002`, `kind: generic`, `layer: 3`. This does not break anything
mechanically (`parents: [SK-INFRA-001, SK-QA-002]` itself is correct and
resolves fine — VR-3 passes), but the prose is now factually wrong about
the state of the library and could mislead a reader into thinking the
cross-cutting security reference is a forward-reference to nothing.
**Recommendation:** remove the "(not yet authored in this library)"
parenthetical in all four locations, and consider adding a proper
`[security-engineering](../security-engineering/SKILL.md)` link in
`SKILL.md`'s prose/References the way this skill already links
`containerization`. Not fixed in this pass — correcting cross-skill
authorship-status prose in four places touches more than the "clear,
narrow" defect categories this review is authorized to fix directly
(missing field / YAML syntax / CE-1 overflow / `depends_on_skills`-
`parents` conflation / VR-5 mismatch / broken cross-reference); flagged
for the skill's owner instead.

No other problems found. `parents: [SK-INFRA-001, SK-QA-002]` matches the
catalog row exactly; the Engine-API/Go-SDK/Build-Checks/Compose-V2/
cgroup-v1/ECI version-sensitive claims all trace precisely to
`research/technologies/docker.md`; the isolation-runtime and Docker-Build-
Cloud decision frameworks both include an explicit simplest/default branch
(runc by default, self-hosting by default) with the over-engineering trap
named in Anti-patterns ("Switching every workload to gVisor/Kata 'for
security'"); Security section correctly forward-references
`security-engineering` for deep threat modeling rather than restating it.

---

## github-actions

**Critical (fixed) — `covered_versions` was a plain string, not the
spec-required `map` type (VR-1).** Per `specification.md` §2.6,
`covered_versions` is typed `map` ("Per component: the version/range this
skill's content is correct for"). Every other technology skill in this
batch (including the other "no single numbered version" skills, `webrtc`
and `websocket-api`) wraps its explanatory text under a component key
(e.g. `webrtc: "1.0 (W3C Recommendation...)"`). `github-actions/skill.yaml`
instead had:

```yaml
covered_versions: >-
  GitHub Actions the product is a continuously-deployed SaaS with no discrete
  release version [Source: docs.github.com/en/actions]; ...
```

— a bare multi-line string scalar, confirmed via `yaml.safe_load` to
parse as `str`, not `dict`, while every sibling skill's `covered_versions`
parses as `dict`. **Fixed**: wrapped the same text under a
`github-actions:` key, matching the `webrtc`/`websocket-api` pattern for
"no single numbered version, but real version-sensitive sub-component
facts." Verified `python3 -c "import yaml; yaml.safe_load(open(...))"`
now returns a `dict` with one key, and the file still parses as valid
YAML overall (ran as the last action touching this file).

No other problems found. `parents: [SK-INFRA-002]` matches the catalog;
the `husky`/`ci-cd-pipeline` boundary is explicit and correctly
cross-referenced (the `HUSKY: 0` CI-skip pattern is named as the concrete
complementary mechanism, not a restatement); the Security section is
appropriately the deepest in the skill (self-hosted-runner risk, cache
poisoning on `pull_request_target`, the `set-output`/`save-state`
log-injection history) and is explicitly framed as GitHub-Actions-specific
content the parent (`ci-cd-pipeline`) does not cover; the Node-20-removal
and artifact-v3→v4 dates trace precisely to the research doc and are
correctly flagged as version-sensitive/imminent as of `last_verified`.

---

## husky

**Medium — Anti-patterns section has no over-engineering pitfall.**
`specification.md` §3.2 item 8 requires the Anti-patterns body section to
include "at least one over-engineering pitfall for the domain." This
skill's five Anti-patterns entries are: relying on Husky alone instead of
lint-staged (an *under*-engineering trap, the opposite direction), leaving
legacy v4-era hook lines unmigrated, installing hooks in CI without
`HUSKY=0`, wiring the wrong lifecycle script for the package manager, and
publishing without guarding install scripts — none of these is "reaching
for more tool/complexity than the task needs." The Decision framework's
point 4 ("Simplest first... don't reach for a heavier hooks framework the
task doesn't need") gestures at the right idea but lives in Decision
framework, not Anti-patterns, so the required section-level content isn't
actually present where the spec asks for it. **Recommendation:** add an
Anti-patterns entry such as "reaching for a heavier hooks framework (or
hand-rolling staged-file filtering beyond Husky+lint-staged) when a
one-line `.husky/pre-commit` already covers the need" to close this gap.

No other problems found. `parents: [SK-INFRA-002, SK-CONV-001]` matches
the catalog; the `git-conventions`/`ci-cd-pipeline` boundary is precisely
stated (Husky fires the hook, it doesn't define the commit-message
convention or the CI gate); every version-sensitive claim (Git >2.9
floor, Node ≥18 for the CLI vs. no-Node-at-runtime, the v10.0.0
compatibility-shim removal) traces to the research doc; the Security
section correctly frames Husky as a developer-convenience, not an
enforcement boundary, and hands off to `ci-cd-pipeline` for the real gate.

---

## jest-vitest

No problems found. `parents: [SK-QA-001]` matches the catalog. The merge
is coherent, not two bolted-together halves: mocking, snapshots, fake
timers, and coverage are each presented Jest-then-Vitest in one continuous
narrative with the genuine semantic differences called out explicitly
(mock-factory default-export convention, `ts-jest` type-checking vs.
`expect-type`'s different guarantee), and `conflicts_with: []` is
correctly justified in a code comment as intentional (choose-one, not
competing tools needing a conflict declaration). The decision framework's
primary signal — check the *other* framework's own documented runner
preference (Mongoose discourages Jest, Prisma recommends it, Vue/
Angular/Nuxt default to Vitest, Next.js supports both) — is a genuinely
useful, non-generic piece of guidance grounded in cross-referenced
sibling research docs, not invented. Version-sensitive claims (Jest
v27/v30 defaults, Vitest v3.2/v5.0 changes) all trace to the two research
docs precisely, including the `expect.arrayOf()`/`vi.when()`/`bench()`
v5.0 additions. Anti-patterns includes an explicit over-engineering entry
("reaching for a full runner migration... on a healthy, green suite").

---

## playwright

No problems found. `parents: [SK-QA-001, SK-FE-004]` matches the catalog
exactly — this is the only skill in the batch with two Layer-3 parents,
and both are correctly reflected in the "When not to use" section
(test-layer selection routes to `testing-strategy`, role-locator/MCP-
accessibility-tree framing routes to `web-accessibility`). This is also
the only Tier-C skill in the batch, and it is the correct one per the
catalog's own note ("browser automation not universal across agents");
`capability_fallbacks.browser` correctly documents the MCP-fallback path
and the final advisory-only degradation, satisfying VR-5. Version-gated
claims (v1.60 API removals, v1.62 stable component-testing model, v1.63
Ubuntu-20.04/experimental-package deprecation) trace to the research doc,
and the macOS-13/Cookie-header claim is correctly flagged as
**unresolved** rather than asserted as settled — matching the research
doc's own uncertainty rather than overclaiming. Security section covers
`storageState` credential leakage and the root-vs-sandboxed Docker
posture with a clear decision rule (untrusted content → non-root+seccomp;
own trusted suite → root is acceptable), matching the source precisely.

---

## opentelemetry

No problems found on this individual re-review. `parents: [SK-QA-004]`
matches the catalog. The API/SDK/Collector three-layer architecture, OTLP
port/transport details, W3C Trace Context + Baggage-is-higher-risk
distinction, and — most importantly for this skill — the per-language,
per-signal stability matrix (traces Stable in 9 languages, logs Stable in
only 3) all trace precisely to the research doc, and the skill correctly
elevates "JS/Python have Stable traces/metrics but Development-status
logs" as the single most consequential version-awareness fact, which is
exactly right given this library's own heavy JS/Python usage elsewhere.
The Testing section honestly reports a real documented gap (no official
"testing your instrumentation" guide was found) rather than inventing
one. `related_skills: [SK-TECH-prometheus, SK-TECH-grafana, SK-TECH-
sentry]` and the reciprocal references on all three siblings are
consistent and correctly note that `opentelemetry.io` itself only
documents Grafana/Sentry as one-line vendor listings, deferring
integration mechanics to each sibling skill.

---

## prometheus

No problems found. `parents: [SK-QA-004]` matches the catalog. Metric-type
semantics (Counter-never-decreases, native-vs-classic histograms with the
Go/Java-only native-histogram-support caveat, Summary's non-aggregatable
quantiles) are stated precisely per the research doc. The "not clustered,
not natively HA" framing is treated as a defining architectural fact with
its own dedicated Knowledge/Anti-patterns/Trade-offs coverage rather than
apologized for, matching the source's own framing. The Alertmanager-HA
"never a load balancer" rule is stated as an explicit engineering rule and
a verification check, correctly citing the "❌ Don't use a load balancer /
✅ Configure all instances in Prometheus" source line. The v2.55/v3.0
TSDB-compatibility boundary is escalation-gated (requires explicit
version confirmation before any upgrade plan), appropriately treating
irreversible data loss as a real risk rather than a footnote. `promtool
test rules` is correctly identified as the actual, documented (not
invented) rule-testing mechanism.

---

## grafana

No problems found. `parents: [SK-QA-004]` matches the catalog. The
"Grafana Alertmanager extends Prometheus Alertmanager; rule evaluation
always happens in Grafana; notification routing can go to either"
distinction — flagged by the task brief as the precise point requiring
accuracy — is stated correctly and matches the research doc's own
careful wording. The v11.0.0 legacy-alerting-removal and v13.0.0
breaking-change/Git-Sync-migration-bug claims are both escalation-gated
(explicit confirmation required before crossing either boundary), which
is appropriate given the research doc's own "existing alerts becoming
inaccessible or lost" and "dashboards and folders... lost" language. The
"LTS-shaped but not officially branded LTS" nuance is preserved rather
than smoothed over. The `related_skills`/parent-skill cross-references to
`prometheus` and `opentelemetry` are reciprocal and consistent with those
two skills' own `related_skills` lists.

---

## sentry

**Medium — Anti-patterns section has no over-engineering pitfall.** Same
pattern as `husky`: the four Anti-patterns entries (assuming `enabled:
false` fully disables the SDK, initializing after other imports, treating
Sentry as a metrics/log backend, shipping a release without Debug IDs)
are all about missing/misordered configuration, not about reaching for
more surface area than the task needs. The Decision framework's point 4
("Simplest first... don't reach for Session Replay, Logs, or custom
tracing until a specific diagnostic gap justifies the added surface and
quota cost") is exactly the right content but, again, lives in Decision
framework rather than being restated as an Anti-patterns entry.
**Recommendation:** add an Anti-patterns entry such as "enabling Session
Replay, Sentry Logs, or a `tracesSampler` before a specific diagnostic gap
justifies the added quota cost — SDK defaults plus the framework error
handler are often sufficient" to close this gap.

No other problems found. `parents: [SK-QA-004]` matches the catalog. This
is the strongest execution of the batch's most safety-critical prior
finding: the v9 Metrics-API-removal claim is present in
`version_sensitive_claims`, in Anti-patterns ("Treating Sentry as a
general metrics or log-aggregation backend"), and in the Unresolved-items
summary, each time correctly stated as *removed entirely*, not merely
deprecated — matching this project's own prior audit language verbatim
("the strongest evidence Sentry is... not a metrics platform"). DSN
public-vs-secret status, the layered PII-scrubbing architecture (SDK
hooks → server-side default → Relay), the `instrument.js`-first
initialization-ordering requirement, and the v7→v8→v9→v10 breaking-change
history (with the full itemized table correctly offloaded to
`references/js-sdk-breaking-changes.md`, which exists and is referenced
correctly) all trace precisely to the research doc. The
Sentry↔OpenTelemetry relationship (JS SDK runs on OTel internally since
v8, and still needs it for context/trace-propagation correctness even
with Sentry's own tracing off) is stated with the exact quoted language
from the research doc.

---

## socketio

**Low (fixed) — broken cross-reference in the Testing section.**
`SKILL.md` (before fix) read: `Deep test-strategy method is owned by
[testing-strategy](../../core/taxonomy/skill-catalog.md).` The link text
says "testing-strategy" but the URL pointed at the taxonomy catalog file,
not the sibling skill's own `SKILL.md` — a reader clicking through lands
on a 300-row taxonomy document instead of the testing-strategy skill.
`skills/testing-strategy/SKILL.md` exists at the expected relative path.
**Fixed**: changed the link target to `../testing-strategy/SKILL.md`.

No other problems found. `parents: [SK-BE-004]` matches the catalog. The
two-layer Engine.IO/Socket.IO architecture, the v2→v3/v3→v4 breaking-
change boundaries (with the important nuance that v3→v4 is server-side
only and v3/v4 clients remain protocol-compatible), and the multi-node
adapter comparison (Redis has no `connectionStateRecovery` support;
MongoDB/Redis Streams do) all trace to the research doc. The
`realtime-communication` parent boundary is respected throughout — the
Decision framework opens by explicitly assuming the parent has already
chosen Socket.IO and asks only "is the added abstraction still earning
its keep," which is a genuinely Socket.IO-specific question, not a
restatement of the parent's transport-comparison. Anti-patterns includes
an explicit over-engineering entry (switching to µWebSockets.js or a
persistence-capable adapter before measuring an actual bottleneck).

---

## webrtc

**Medium — Anti-patterns section has no over-engineering pitfall.**
The five Anti-patterns entries (leaving `plan-b` `sdpSemantics` in place,
not setting `iceTransportPolicy: "relay"` when privacy matters, oversized
data-channel messages, asymmetric caller/callee negotiation logic,
STUN-only NAT traversal) are all under-engineering/missing-safety traps,
not over-engineering ones. The Decision framework's point 1 ("Is
peer-to-peer actually required, given what it costs?" — building
signaling and TURN infrastructure you wouldn't need with a server-mediated
transport) is the domain's real over-engineering trap, but it is not
restated in Anti-patterns. **Recommendation:** add an Anti-patterns entry
such as "reaching for WebRTC (and the signaling/TURN infrastructure it
requires) when the feature doesn't actually need true peer-to-peer media/
data — a server-mediated transport is simpler whenever the server can
legitimately see/process the data."

**Medium — missing security caveat on TURN credential exposure.** The
Knowledge/Configuration section shows the standard `iceServers`
configuration example with `username`/`credential` fields inline in
client-constructed `RTCConfiguration` JavaScript. The Security section
covers DTLS-SRTP, certificate-reuse constraints, IP-address exposure via
`iceTransportPolicy`, and "impact on local network," but never notes that
static TURN credentials placed in that client-side config object are
visible to anyone who can inspect the client (dev tools, a decompiled
bundle, a network capture of the signaling exchange) — a basic,
architecture-level consequence of where the credential lives, distinct
from the credential-*rotation-scheme* question the research doc itself
flags as "not officially documented" (`research/technologies/webrtc.md`
§7, "Unresolved"). The task brief specifically calls out "TURN/STUN
credential exposure" as a category worth checking for this skill, and it
is absent. **Recommendation:** add a line to Security noting that static/
long-lived TURN credentials embedded in client-visible `RTCConfiguration`
are inherently exposed to the client, and that time-limited/rotating
credentials (the shape the research doc found only in secondary,
non-official sources) are the mitigation to reach for in production — or,
if staying strictly within what's officially documented, at minimum
flag the exposure fact itself, which follows directly from the
`RTCConfiguration` API shape already shown in this skill's own example.

**Low (fixed) — two broken cross-references.** `SKILL.md` had `Cross-
cutting threat modeling beyond this is owned by
[security-engineering](../../core/taxonomy/skill-catalog.md)` (Security
section) and `Deep test-strategy method beyond this WebRTC-specific CI
setup is owned by [testing-strategy](../../core/taxonomy/skill-catalog.
md)` (Testing section) — both link text/target mismatches identical to
the `socketio` and `websocket-api` instances. **Fixed**: retargeted to
`../security-engineering/SKILL.md` and `../testing-strategy/SKILL.md`
respectively; both target files exist.

No other problems found. `parents: [SK-BE-004]` matches the catalog. The
perfect-negotiation pattern (polite/impolite roles, `makingOffer`/
`isSettingRemoteAnswerPending` state), the Plan-B→Unified-Plan Chrome
M65→M96 timeline, ICE restart mechanics, and the RTCDataChannel
head-of-line-blocking caveat all trace precisely to the research doc.
Codec-support-by-browser-version claims are correctly flagged
point-in-time/re-verify-before-relying-on rather than stated as
permanently current, matching VA-3.

---

## websocket-api

**Low (fixed) — two broken cross-references.** `SKILL.md` had `Deep
performance method is owned by [performance-engineering](../../core/
taxonomy/skill-catalog.md)` (Performance section) and `Deep test-strategy
method is owned by [testing-strategy](../../core/taxonomy/skill-catalog.
md)` (Testing section) — the same link text/target mismatch pattern found
in `socketio` and `webrtc`. **Fixed**: retargeted to
`../performance-engineering/SKILL.md` and `../testing-strategy/SKILL.md`
respectively; both target files exist.

No other problems found. `parents: [SK-BE-004]` matches the catalog. RFC
6455 handshake mechanics (the exact `Sec-WebSocket-Accept` computation),
the client-must-mask/server-must-not-mask security rule, the three
close codes that are "never actually sent on the wire" (1005/1006/1015)
and the resulting distinction between a locally-synthesized close reason
and a genuine remote one, and the Node.js client-only gap (with the
precise v21.0.0-experimental → v22.4.0-stable version history) all trace
precisely to the research doc. The "no official test framework for
consumers" and "no JS-level ping/pong API" gaps are both stated honestly
as real documented absences rather than papered over. Anti-patterns
includes an explicit over-engineering entry (reaching for
`WebSocketStream` or a full client library before trying plain
`bufferedAmount` monitoring).

---

## What was fixed vs. what was only reported

**Fixed directly (5 files touched, all narrow and mechanical):**
- `skills/github-actions/skill.yaml` — `covered_versions` converted from a
  bare string to the spec-required `map` shape (VR-1).
- `skills/socketio/SKILL.md` — 1 broken cross-reference retargeted.
- `skills/webrtc/SKILL.md` — 2 broken cross-references retargeted.
- `skills/websocket-api/SKILL.md` — 2 broken cross-references retargeted.

Every edited `skill.yaml` was re-validated with
`python3 -c "import yaml; yaml.safe_load(open('<path>'))"` as the last
action touching that file; all pass.

**Reported only, not fixed** (architecture/content judgment calls outside
this review's narrow-fix mandate): the `docker` stale-authorship-status
prose (4 locations), and the three "Anti-patterns section lacks an
explicit over-engineering entry" findings (`husky`, `sentry`, `webrtc`),
plus the one missing-security-caveat finding (`webrtc`). None of these
touch `parents`, scope, or any already-documented architectural decision;
they are flagged for the skills' owner to address as content additions.
