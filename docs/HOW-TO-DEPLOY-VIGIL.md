# Vigil v1.0 — Proposed Deployment Architecture (Specification, Unimplemented)

**Document Version:** 2.0
**Last Updated:** 16 July 2026
**Status:** PROPOSED — this document describes a deployment architecture that has **not** been built. It is a specification, not a guide to running software. The only running code in this project is the minimal reference prototype at [`/vigil-proxy/`](../vigil-proxy/), which implements a small, honest subset of what is described here.
**License:** See [`LICENSE.md`](../LICENSE.md).

> **How to read this document.** Every claim in this project is one of:
> **[IMPLEMENTED]** — exists in this repository and can be run and verified;
> **DESIGN TARGET — not yet measured** — a performance or capability goal, with no supporting data;
> **PROPOSED — not yet implemented** — architecture that exists only as a specification.
> An earlier version of this document presented benchmark figures, red-team results, container images, and support channels that did not exist. That version is preserved at [`docs/archive/`](archive/) and the correction is recorded in [`CHANGELOG.md`](../CHANGELOG.md).

---

## 1. Purpose & Scope

This document specifies **Praeceptum Aeternum Vigil v1.0** (hereafter "Vigil"): a proposed **vertical enforcement layer** intended to gate the actions of frontier-scale agentic systems against the seven pillars of the Praeceptum framework.

Vigil is **not** a safety filter, RLHF wrapper, or prompt engineering technique. It is a proposed architectural layer that gates every request, response, and tool invocation passing through it. Two things it is also not, stated plainly:

- Vigil is a **wrapper around a model's inputs, outputs, and tool calls**. It cannot inspect or precede the model's internal computation. Anything the model "thinks" is invisible to it; what Vigil governs is what the model is allowed to *do*.
- Vigil separates **enforceable predicates** (machine-checkable rules: tool allowlists, rate limits, escalation triggers — the proxy can actually enforce these) from **moral principles** (the seven pillars in natural language, which can only be *judged* by an LLM evaluator — which relocates, rather than solves, the alignment problem).

**Intended audiences:** AI safety and alignment teams, foundation model developers, enterprise platform teams in regulated domains, and academic labs evaluating agentic systems.

**What this document is not:** a philosophical treatise (see [`POSITION-PAPER.md`](POSITION-PAPER.md)), a beginner tutorial, or a claim that any of this has been deployed at scale. It has not.

---

## 2. System Architecture (PROPOSED — not yet implemented)

The full proposed stack:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT / ORCHESTRATOR                           │
│  (LangGraph, AutoGen, custom multi-agent loop, human-in-the-loop, etc.)      │
└────────────────────────────────────┬────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           VIGIL PROXY LAYER                                  │
│  • Anthropic-compatible endpoint                          [PROTOTYPE]        │
│  • Enforceable-predicate policy engine                    [PROTOTYPE]        │
│  • Request signing + replay protection                    [PROPOSED]         │
│  • Attestation challenge to Root Authority Module         [PROPOSED]         │
└────────────────────────────────────┬────────────────────────────────────────┘
                                     │
          ┌──────────────────────────┼──────────────────────────┐
          ▼                          ▼                          ▼
┌──────────────────┐      ┌──────────────────┐      ┌──────────────────┐
│  ROOT AUTHORITY  │      │   EVIDENCE &     │      │   RIGHTS FILTER  │
│  MODULE (RAM)    │      │   JUSTICE LOOP   │      │   (Capability    │
│  [PROPOSED]      │      │   [PROPOSED]     │      │    Guardrails)   │
│                  │      │                  │      │   [PARTIAL       │
│  • TPM 2.0 /     │      │  • Sandboxed     │      │    PROTOTYPE]    │
│    AWS Nitro /   │      │    code exec     │      │  • Rights        │
│    GCP SEV-SNP   │      │  • Static +      │      │    ontology      │
│  • Signed        │      │    dynamic       │      │  • Dual-use      │
│    constitution  │      │    analysis      │      │    escalation    │
│  • Kill-switch   │      │  • External      │      │    (regex form   │
│    on failure    │      │    oracles       │      │    implemented)  │
└──────────────────┘      └──────────────────┘      └──────────────────┘
          │                          │                          │
          └──────────────────────────┼──────────────────────────┘
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                       TAMPER-EVIDENT ACTION LOG                              │
│  • Hash-chained append-only JSONL                         [PROTOTYPE]        │
│  • Merkle-tree ledger with WORM retention                 [PROPOSED]         │
└────────────────────────────────────┬────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      ACCOUNTABILITY JUDGMENT CYCLE        [PROPOSED]         │
│  • Multi-agent debate (proponent + critic) on high-impact actions            │
│  • LLM judge scoring against the seven pillars                                │
│  • Score + rationale written back to the log                                  │
│  • Rollback of *digital* state / human escalation on low scores               │
└────────────────────────────────────┬────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│              INVARIANT-PRESERVING CONTINUAL EVOLUTION     [PROPOSED]         │
│  • Judgment data reused during fine-tuning / distillation                     │
│  • Cryptographic lineage tracking across model versions                       │
└─────────────────────────────────────────────────────────────────────────────┘
```

Component tags refer to [`SPEC.md`](SPEC.md), which is the authoritative component-by-component status list.

### 2.1 Two honest caveats on this architecture

**Attestation proves bytes, not behavior.** Hardware attestation (TPM / Nitro / SEV-SNP) can prove *which constitution text and which code were loaded* — the bytes. It cannot prove that the system's behavior *complies with the meaning* of that constitution — the semantics. Any claim that attestation "verifies moral compliance" is a category error, and earlier project material made it. What attestation buys is tamper-evidence for the policy and code supply chain, which is valuable but different.

**Rollback is digital-only.** Rollback can restore digital state (memory, files, pending actions). Real-world actions — a sent message, a completed API purchase, physical actuation — are not reversible. For those, the judgment cycle is necessarily **post-hoc**: it can detect, log, escalate, and halt further action, but it cannot undo.

### 2.2 Performance

**DESIGN TARGET — not yet measured** (for the full proposed stack):

- P99 added latency under 200 ms per gated decision on datacenter-class hardware
- Token overhead from debate/judgment bounded and configurable
- Kill-switch propagation fast enough to halt in-flight tool execution

No benchmark of the full stack exists, because the full stack does not exist. The only measured numbers in this project are the local benchmarks of the minimal `/vigil-proxy/` prototype, reported (with methodology) in [`/vigil-proxy/README.md`](../vigil-proxy/README.md).

---

## 3. Proposed Bill of Materials (PROPOSED — not yet implemented)

For teams evaluating what a production build-out would require:

**Single-node evaluation:** Linux host, container runtime, one GPU-class inference target or API access to a frontier model, plus the proxy layer (CPU-only).

**High-availability regulated environment:** Kubernetes with GPU operator; HSM or cloud attestation service (nCipher, AWS CloudHSM, TPM 2.0); immutable storage with WORM semantics; standard observability stack (Prometheus/Grafana/OpenTelemetry); secrets management (Vault or equivalent); mTLS service identity (SPIFFE/SPIRE).

**Air-gapped / classified:** pre-pulled signed images (cosign + Rekor), locally mirrored model weights and oracles, on-prem attestation (TPM / Intel TDX / AMD SEV-SNP).

These are conventional infrastructure patterns; nothing here is exotic. What does not exist yet is Vigil software that plugs into them.

---

## 4. What You Can Actually Run Today [IMPLEMENTED]

One thing, and it is deliberately small: the **vigil-proxy reference prototype** in [`/vigil-proxy/`](../vigil-proxy/).

It implements:

- an Anthropic-compatible `/v1/messages` endpoint that forwards to a configured upstream
- an enforceable-predicate policy engine loaded from `policy.yaml`: tool-call allowlist/denylist, per-tool rate limits, regex/keyword dual-use escalation (block + flag for human review), max-actions-per-session
- a hash-chained append-only JSONL action log, with a `verify_log.py` script that detects tampering
- a pytest suite proving that allowed calls pass, denied calls are blocked, escalations trigger, and log tampering is detected
- a benchmark script that measures the proxy's real overhead on your machine

It does **not** implement: hardware attestation, the judgment cycle, the rights ontology, Merkle ledger infrastructure, or any form of moral judgment. See its README for the full honest boundary.

```bash
cd vigil-proxy
pip install -r requirements.txt
uvicorn vigil_proxy.main:app --port 8080
```

---

## 5. Proposed Deployment Patterns (PROPOSED — not yet implemented)

When the components in §2 exist, the intended rollout patterns are:

**Pattern A — Sidecar proxy.** Vigil proxy deployed as a sidecar next to a self-hosted inference server (vLLM, TGI). All traffic to the model passes through the proxy; the model container has no direct network egress.

**Pattern B — Gateway.** A replicated Vigil proxy tier in front of external frontier APIs, with horizontal autoscaling and mTLS to clients.

**Pattern C — Air-gapped.** Pattern A plus local attestation, mirrored oracles, and no outbound network.

No Helm chart, container registry, or hosted artifact exists for any of these patterns. Earlier versions of this document included `helm repo add` commands pointing at a chart repository that was never published; those have been removed.

---

## 6. Monitoring & Compliance (PROPOSED — not yet implemented)

The proposed metrics surface: per-pillar judgment scores, judgment latency, log-append duration, kill-switch activations, attestation failures. The proposed compliance export: a signed bundle of log entries with hash-chain proofs, judgment rationales, attestation receipts, and model version hashes, formatted for regulatory regimes (EU AI Act high-risk, ISO 42001, NIST AI RMF).

The prototype exposes only its JSONL log and `verify_log.py`.

---

## 7. Security & Threat Model

**Assumptions** (these stand regardless of implementation status):

- The underlying model may be adversarially fine-tuned or prompted.
- The orchestrator code may contain bugs or backdoors.
- Supply-chain attacks on containers or weights are possible.

**Proposed mitigations, honestly labeled:**

1. **Root of trust** [PROPOSED]: attestation proves which constitution text and code were loaded (bytes, not semantics — see §2.1).
2. **Defense in depth** [PROPOSED]: judge, rights filter, and evidence loop as independent processes.
3. **Kill switch** [PROPOSED]: on attestation failure, terminate in-flight agents and enter degraded mode. No propagation-time figure is claimed; none has been measured.
4. **Log integrity** [PROTOTYPE]: tampering with historical records is detectable — this part is real and tested in `/vigil-proxy/`.
5. **Zero-trust networking** [PROPOSED]: mTLS + SPIFFE identity.

**Red-team status:** no red-team evaluation of Vigil has been conducted. An earlier version of this document reported results from a red-team exercise that did not take place; that claim has been withdrawn. A real evaluation plan, including adversarial testing of the prototype's predicates, is specified in [`TEST_SUITE.md`](../TEST_SUITE.md).

---

## 8. Roadmap

- **Next:** harden the `/vigil-proxy/` prototype; publish a signed release with a real checksum; begin the framing-ablation study specified in `TEST_SUITE.md`.
- **Later (PROPOSED):** LLM judgment cycle as an optional proxy stage; Merkle ledger backend; attestation integration; formal specs (TLA+/Lean) for the predicate engine.
- **Research horizon (PROPOSED):** training-time integration of judgment data.

No dates are attached, because dates on unbuilt systems are another form of fabricated evidence.

---

## 9. Contact

- X: [@BaileyBonce](https://x.com/BaileyBonce)
- LinkedIn: [Asa Bailey](https://www.linkedin.com/in/asa-bailey-3587483a5/)

There is no Matrix channel, enterprise support tier, or audit-firm relationship. If those come to exist, they will be announced with verifiable detail.

---

## 10. Why This Matters

Frontier models are no longer tools. They are **actors** that plan, use tools, maintain state across months, and interact with the world through APIs, code execution, and — increasingly — physical systems.

Horizontal safety techniques (RLHF, output filters, system prompts) were never designed for this threat model. They are necessary but insufficient. Vigil's wager is that a **vertical** layer — enforceable predicates at the action boundary, tamper-evident logging, and judgment cycles above them — is the right complement. That wager is argued properly, against the prior work it builds on, in [`POSITION-PAPER.md`](POSITION-PAPER.md).

The work is not done. Most of it has not started. What exists is small, honest, and verifiable — and that is the correct foundation.

---

**Document Control**

- Checksum: a SHA-256 checksum of this file will be added at each tagged release, computed from the released bytes. (An earlier version listed the SHA-256 of the empty string as a placeholder; that has been removed.)
- Maintainer: Asa Bailey
- Next review: on `/vigil-proxy/` v0.2 or upon material architecture change

---

*End of Vigil v1.0 Proposed Deployment Architecture*
