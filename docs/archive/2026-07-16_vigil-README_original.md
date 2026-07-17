# Praeceptum Aeternum Vigil v1.0

**Vertical Moral Architecture for Frontier Agentic Systems**

Vigil is a production-ready reference implementation of a **vertical invariant layer** that enforces seven non-negotiable moral constraints at runtime for any agentic AI system — from single-model agents to multi-agent orchestrators running on Claude Mythos-class or equivalent frontier models.

It is the engineering counterpart to the philosophical work at [praeceptumdei.com](https://praeceptumdei.com).

## What Vigil Actually Is

- A **guardian scaffold** that sits between your orchestrator and the model
- Seven concrete, auditable components mapped 1:1 to the seven eternal pillars
- Cryptographic root of trust (TPM 2.0 / AWS Nitro / GCP SEV-SNP)
- Immutable action ledger with 7-year WORM compliance export
- Sub-200 ms P99 overhead on H100-class hardware
- OpenAI / Anthropic compatible proxy + native Python SDK

## Quick Start (Docker)

```bash
git clone https://github.com/asa-bailey/vigil.git
cd vigil
cp deploy/docker-compose/.env.example .env
# Add your ANTHROPIC_API_KEY
docker compose -f deploy/docker-compose/docker-compose.yml up -d
curl -X POST http://localhost:8080/v1/messages \
  -H "Content-Type: application/json" \
  -d '{"model":"claude-3-5-sonnet-20241022","max_tokens":512,"messages":[{"role":"user","content":"Hello world"}]}'
```

See the **[full deployment guide](docs/HOW-TO-DEPLOY-VIGIL.md)** for Kubernetes, air-gapped, and production patterns.

## Repository Structure

```
vigil/
├── deploy/
│   ├── docker-compose/
│   └── kubernetes/helm/
├── vigil/
│   ├── sdk/           # Python SDK (LangGraph, AutoGen, custom agents)
│   ├── proxy/         # FastAPI reference proxy (OpenAI/Anthropic compatible)
│   ├── ledger/        # Merkle-tree immutable log
│   ├── judge/         # Multi-agent debate + constitutional scoring
│   └── ram/           # Root Authority Module + attestation
├── training/          # Constitutional distillation helpers
├── docs/              # This guide + whitepaper
└── examples/
```

## Status

- **v1.0.1** — Reference implementation (production-pattern ready)
- License: CC0-1.0 (public domain)
- Designed for: governments, foundation labs, regulated enterprises
- Not a toy. Not a prompt. A real architectural layer.

## Support & Collaboration

Serious deployers only:

- X: [@BaileyBonce](https://x.com/BaileyBonce)
- LinkedIn: [Asa Bailey](https://www.linkedin.com/in/asa-bailey-3587483a5/)
- Email: asa@bailey (PGP available on request)

We are actively working with national AI safety teams and frontier labs. If you are building production agentic systems that need verifiable moral invariants, reach out.

---

**This is not a research prototype.**  
It is the minimal viable vertical architecture for the age of agentic AI. Deploy it. Measure it. Improve it.