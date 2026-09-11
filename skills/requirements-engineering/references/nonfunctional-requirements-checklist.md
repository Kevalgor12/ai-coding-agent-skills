# Non-functional requirements checklist (Tier-2 reference)

Loaded only when [SKILL.md](../SKILL.md) links here — a request's
non-functional shape is unclear, or a full elicitation pass is warranted per
the skill's decision framework. Not every category applies to every request;
run through it, don't force every row to produce a requirement.

For each category: what to check, and a sample prompting question if it's not
already answered by the request.

| Category | Check for | Prompting question |
|---|---|---|
| **Scale / load** | Expected concurrent users, request rate, data volume, growth trajectory. | "Roughly how many users/requests does this need to handle, now and in a year?" |
| **Latency / performance budget** | A stated or implied response-time expectation. | "Is there a response-time expectation, or a point past which it's 'too slow'?" |
| **Availability / reliability** | Acceptable downtime, disaster-recovery expectation, criticality of the feature. | "If this is down for an hour, what happens? Does that change your answer?" |
| **Security posture** | Auth requirements, data sensitivity classification, threat model (public internet vs. internal-only). | "Does this touch sensitive data, or need to be restricted to certain users/roles?" |
| **Compliance / legal** | Regulatory regime (GDPR, HIPAA, PCI-DSS, SOC2, accessibility law), data residency, retention/deletion obligations. | "Is any of this data regulated, or does it need to meet a specific compliance standard?" |
| **Accessibility** | Target conformance level (e.g. WCAG 2.2 AA), assistive-technology support expected. | "Is there an accessibility standard this needs to meet?" |
| **Internationalization / localization** | Target locales, languages, RTL support, currency/date formats. | "Does this need to support more than one language/region?" |
| **Deployment environment** | Target infrastructure, network constraints (air-gapped, on-prem, existing cluster), release cadence. | "Where does this run, and does it need to fit an existing deployment setup?" |
| **Observability** | What "working correctly in production" needs to be verifiable as; who needs to see it. | "How will you know this is working correctly once it's live?" |
| **Cost ceiling** | An explicit or implied budget constraint on infrastructure/third-party services. | "Is there a cost constraint that should rule out certain approaches?" |
| **Backward compatibility** | Whether existing consumers (API clients, integrations, data formats) must keep working. | "Does anything currently depend on the existing behavior/shape of this?" |

## Using this without over-eliciting

This table is a *prompt bank*, not a mandatory questionnaire. For a
low-stakes, easily-reversible task, skim it mentally and move on if nothing
jumps out — asking all eleven questions for a copy tweak is the
over-elicitation anti-pattern the parent skill warns against. For a new
system, a public-facing feature, or anything touching sensitive data, walk it
deliberately; the categories most often missed by requesters (compliance,
observability, backward compatibility) are exactly the ones worth checking
even when nothing in the request hints at them.
