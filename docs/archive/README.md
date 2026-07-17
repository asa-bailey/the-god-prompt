# Archive

This directory preserves material removed from the active repository during the
July 2026 credibility remediation (see `/CHANGELOG.md`). Nothing here should be
treated as accurate documentation of a working system.

Why these files were archived rather than deleted: the project's governing rule
is that nothing substantial is lost, and the original documents remain available
for anyone auditing the history of the project's claims.

| File / directory | What it was | Why it was archived |
|---|---|---|
| `2026-07-16_HOW-TO-DEPLOY-VIGIL_original.md` | Original "Production Deployment Guide" | Contained unmeasured benchmark figures presented as results, and references to infrastructure (Helm repo, container images, judge model, audit relationships) that does not exist. Replaced by the honest specification at `docs/HOW-TO-DEPLOY-VIGIL.md`. |
| `2026-07-16_vigil-README_original.md` | Original `vigil/README.md` | Described the mock code as "production-ready" with performance claims that were never measured. |
| `2026-07-16_vigil-pyproject_original.toml` | Packaging metadata for the mock SDK | Pointed at a separate `asa-bailey/vigil` repository that does not exist. |
| `vigil-deploy-unimplemented/` | Docker Compose + Helm chart | Referenced container images (`vigil/proxy:1.0.1`, `vigil/ledger:1.0.1`, `vigil/judge:34b-instruct`) and a `vigil-judge-34b` model that were never built or published. |
| `vigil-mock-code/` | FastAPI proxy + Python SDK mock | Returned hard-coded pillar scores and a fake attestation hash, giving the appearance of enforcement that did not occur. A real, minimal, honest reference implementation now lives at `/vigil-proxy/`. |
