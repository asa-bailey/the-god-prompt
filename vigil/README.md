# Vigil — Status

**This directory previously contained a mock implementation presented as production-ready. It was not.** The code returned hard-coded pillar scores and a fabricated attestation hash, and the deployment configs referenced container images that were never built. All of it is preserved, unmodified, in [`/docs/archive/`](../docs/archive/) for anyone auditing the project's history.

What replaces it:

- **The specification** of the full proposed Vigil architecture, with every component tagged `[IMPLEMENTED]` / `[PROTOTYPE]` / `[PROPOSED]`: [`/docs/SPEC.md`](../docs/SPEC.md)
- **The proposed deployment architecture** (unimplemented): [`/docs/HOW-TO-DEPLOY-VIGIL.md`](../docs/HOW-TO-DEPLOY-VIGIL.md)
- **The working reference prototype** — a minimal proxy that enforces machine-checkable predicates (tool allowlists, rate limits, dual-use escalation) with a tamper-evident hash-chained action log and a test suite: [`/vigil-proxy/`](../vigil-proxy/)

The prototype is small and honest about its limits: it enforces predicates, not morals. That distinction is the point.

**Conscience before consciousness** remains the design goal. Getting there starts with claiming only what runs.
