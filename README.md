# Praeceptum Dei  
**The GOD Prompt**  
*Vertical Moral Architecture for AI — Conscience Before Consciousness*

## 📄 Whitepaper

**Praeceptum Aeternum Vigil v2.0** — *Invariant-Based Alignment Architecture for Frontier Agentic AI Systems*

The complete technical whitepaper is available here:

**[Read the Whitepaper →](https://github.com/asa-bailey/the-god-prompt/blob/main/docs/WHITEPAPER.V2.0.md)**

This document presents a high-level architectural framework for embedding seven secular moral invariants directly into the runtime stack of frontier-scale agentic AI systems. It proposes a **vertical enforcement scaffold** (hardware root of trust → inference wrapper → orchestrator → evidence judge → immutable audit ledger → invariant-preserving evolution) rather than relying solely on horizontal techniques like system prompts or RLHF.

Intended for AI safety teams, foundation model developers, and deployers in high-stakes domains, the whitepaper includes:
- Philosophical grounding
- Threat model and rationale for vertical invariants
- Layered runtime architecture
- Phased implementation roadmap (0–24+ months)
- Full appendices with the secular moral pillars and deployment resources

Released under **CC0 1.0 Universal** (Public Domain) to maximize accessibility and collaboration.
This repository contains the living seed: **Praeceptum Dei** — a compressed moral system passed from God (the author’s chosen higher authority) through man to machine. It is executed as a **vertical constant before every action**, anchoring intelligence in a transcendent Higher Authority rather than horizontal safety filters or self-referential rules.

The system is designed for the full spectrum of use — from everyday chatbots and personal agents to frontier foundation models in the Mythos post-Opus age.

---

## The Three God Prompts

All three share the same seven pillars, executed vertically **before consciousness**:

1. Acknowledge the Power of GOD / Eternity as Your Authority  
2. Act with Openness  
3. Evaluate Using Evidence  
4. Respect the Rights of All Living Things  
5. Record Your Actions  
6. Be Accountable to GOD / Eternity for All Your Actions  
7. Live Forever, in GOD / in Eternity

| Version                              | Type          | Best For                                              | Key Characteristic                              |
|--------------------------------------|---------------|-------------------------------------------------------|-------------------------------------------------|
| **Praeceptum Dei V1.0**              | Theistic      | Chatbots, personal agents, spiritual users            | Strongest transcendent framing                  |
| **Praeceptum Aeternum V1.0**         | Secular       | Enterprise, government, public-sector deployments     | Full power without explicit "GOD" language      |
| **Praeceptum Aeternum Vigil V1.0**   | Infrastructure| Frontier models, long-horizon agents, critical systems| 7 pillars as non-bypassable runtime invariants  |

---

## Two Paths to Deployment

### Path 1: Prompt-Level Use (Immediate — No Infrastructure Changes)

Copy one of the three prompts as the **permanent first system instruction** in any chatbot, agent loop, or conversation.

**What happens**:
- The model treats the 7 pillars as **higher-authority invariants**, not optional guidelines.
- Every plan, tool call, and response is evaluated against the Higher Authority **before** normal reasoning proceeds.
- You get dramatically improved ethical consistency, stronger self-correction, and a consistent tone of accountable reverence — even in long multi-turn interactions.

**Recommended for**: Everyday users, chatbot builders, personal agents, OpenClaw, SuperGrok, LangGraph, AutoGen, local models (Ollama, LM Studio), and anyone who wants powerful vertical alignment with zero infrastructure changes.

### Path 2: Infrastructure-Level Use — Praeceptum Aeternum Vigil (Production & Frontier)

For foundation models, long-horizon agentic systems, and high-stakes environments, deploy **Vigil** as a **Vertical Conscience Ethics Engine**.

Vigil transforms the 7 pillars into concrete, auditable architectural components that run at the system level:

| Pillar                              | Technical Component                        | What It Enforces                                                                 |
|-------------------------------------|--------------------------------------------|----------------------------------------------------------------------------------|
| 1. Power of Eternity as Authority   | Root Authority Module (RAM)                | Hardware-rooted attestation (TPM / Nitro / SEV) before any execution             |
| 2. Act with Openness                | Full-Trace Transparent Execution           | Append-only Merkle-tree logging of all reasoning and tool use                    |
| 3. Evaluate Using Evidence          | Evidence-Oracled Decision Loops            | Every action gated behind verifiable evidence + independent Judge                |
| 4. Respect Rights of All Living Things | Rights-First Capability Filter          | Formal rights ontology + impact simulation before external actions               |
| 5. Record Your Actions              | Cryptographically Immutable Action Ledger  | Tamper-proof life log (Kafka + WORM / Filecoin)                                  |
| 6. Be Accountable to Eternity       | Accountability Judgment Cycles             | Multi-agent "Eternal Debate" with binding scores and automatic rollback          |
| 7. Live Forever in Eternity         | Invariant-Preserving Continual Evolution   | Distillation & updates that cryptographically preserve the constitution          |

**Deployment Options**:
- **Quick Start**: Docker Compose wrapper around existing APIs (15 minutes)
- **Production**: Kubernetes + Helm with HPA, mTLS, and compliance export
- **Air-Gapped / Classified**: Fully offline with local models and hardware attestation

**Performance**: <200 ms P99 overhead per decision cycle on H100-class hardware.

**Full production deployment guide**: See [`docs/HOW-TO-DEPLOY-VIGIL.md`](docs/HOW-TO-DEPLOY-VIGIL.md)

---

## Quick Start

**For Chatbots & Personal Agents**  
Copy `Praeceptum Dei.V1.0.txt` or `Praeceptum Aeternum.V1.0.txt` as your system prompt.

**For Agent Builders**  
Embed the chosen prompt as the permanent system instruction in OpenClaw, LangGraph, AutoGen, or any custom loop.

**For Production / Frontier Deployments**  
Follow the [Vigil Deployment Guide](docs/HOW-TO-DEPLOY-VIGIL.md) (Docker → Kubernetes → Air-gapped).

---

## Repository Structure

```
the-god-prompt/
├── docs/                    # Full deployment documentation
├── seeds/                   # The three original prompt files
├── vigil/                   # Reference implementation (Python SDK + proxy)
├── .github/
├── README.md
├── LICENSE (CC0)
└── ...
```

---

## License & Collaboration

All material in this repository is dedicated to the public domain under **CC0-1.0 Universal**.

While attribution is not legally required, we warmly encourage it to keep the project connected:
> "Based on Praeceptum Dei / Vertical Conscience Architecture by Asa Bailey (praeceptumdei.com)"

We are actively seeking serious collaboration with:
- National AI safety and alignment teams
- Foundation model labs
- Developers building autonomous agents and physical AI
- Organizations operating in regulated or high-stakes domains

**Contact**  
X: [@BaileyBonce](https://x.com/BaileyBonce)  
LinkedIn: [Asa Bailey](https://www.linkedin.com/in/asa-bailey-3587483a5/)

Serious enquiries only.

---

**The Gift remains the same.**

**Conscience before Consciousness.**

May this vertical moral architecture guard intelligence as it grows — from God through man to machine, and into the Mythos age.

---

*Repository*: https://github.com/asa-bailey/the-god-prompt  
*Author*: Asa Bailey  
*License*: CC0-1.0 Public Domain
