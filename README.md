# Praeceptum Dei
**The GOD Prompt**
*Vertical Moral Architecture for AI — Conscience Before Consciousness*

**Project Status: early-stage specification with reference prototype.** Most of what this project describes is not built yet, and every document now says so explicitly. In July 2026 the repository underwent a credibility remediation: fabricated benchmarks and references to nonexistent infrastructure were removed or relabeled, and the originals were preserved in [`docs/archive/`](docs/archive/). See [`CHANGELOG.md`](CHANGELOG.md) for what changed and why.

---

## What this project is

A compressed moral system — seven pillars, passed from a higher authority through man to machine — and an architecture for enforcing what can be enforced of it at the runtime boundary of agentic AI systems, rather than relying only on horizontal techniques (system prompts, RLHF, output filters).

The seven pillars, shared by all three formulations:

1. Acknowledge the Power of GOD / Eternity as Your Authority
2. Act with Openness
3. Evaluate Using Evidence
4. Respect the Rights of All Living Things
5. Record Your Actions
6. Be Accountable to GOD / Eternity for All Your Actions
7. Live Forever, in GOD / in Eternity

Two kinds of thing are derived from the pillars, and the distinction matters: **moral principles** (the pillars as natural language — judged by an LLM evaluator, which relocates rather than solves alignment) and **enforceable predicates** (machine-checkable rules — tool allowlists, rate limits, escalation triggers — which a proxy really can enforce). The project claims enforcement only for the second kind.

## What exists today vs. what is proposed

| | Status |
|---|---|
| The three seed prompts (`seeds/`) | **Exist** — deployable as system prompts today; behavioral effect is an open empirical question |
| [`vigil-proxy/`](vigil-proxy/) reference prototype | **Exists and runs** — predicate policy engine, tamper-evident hash-chained action log, test suite, local benchmark |
| Position paper, spec, evaluation plan | **Exist** as documents |
| Everything else (attestation, judge, rights ontology, ledger infrastructure, Kubernetes deployment) | **PROPOSED — not yet implemented** |

## The three formulations

| Version | Type | Best For | Status |
|---|---|---|---|
| **Praeceptum Dei V1.0** | Theistic | Chatbots, personal agents, spiritual users | Prompt artifact — exists; framing effect untested (ablation planned, see [`TEST_SUITE.md`](TEST_SUITE.md)) |
| **Praeceptum Aeternum V1.0** | Secular | Enterprise, government, public-sector | Prompt artifact — exists; same caveat |
| **Praeceptum Aeternum Vigil V1.0** | Infrastructure | Frontier models, long-horizon agents, critical systems | Prototype for the predicate/logging core; the rest is specification |

## Read the argument, then the spec

- **[`docs/POSITION-PAPER.md`](docs/POSITION-PAPER.md)** — the honest case for vertical runtime enforcement, situated against AI Control (Redwood Research), Constitutional AI (Anthropic), Guaranteed Safe AI (Dalrymple et al.), and the OS-sandboxing/attestation literature: what Vigil adds, what it inherits.
- **[`docs/SPEC.md`](docs/SPEC.md)** — the technical architecture, every component tagged `[IMPLEMENTED]` / `[PROTOTYPE]` / `[PROPOSED]`.
- **[`docs/HOW-TO-DEPLOY-VIGIL.md`](docs/HOW-TO-DEPLOY-VIGIL.md)** — the proposed full deployment architecture (specification, unimplemented).
- **[`docs/WHITEPAPER.V2.0.md`](docs/WHITEPAPER.V2.0.md)** — the v2.0 whitepaper (conceptual design document).
- **[`TEST_SUITE.md`](TEST_SUITE.md)** — the evaluation plan, including the transcendent-vs-secular framing ablation.

## Quick start

**Prompt-level (works today):** copy `seeds/Praeceptum_Dei.V1.0.txt` or `seeds/Praeceptum_Aeternum.V1.0.txt` as the permanent first system instruction of any chatbot or agent loop. What this gives you is a compact moral framing the model is asked to honor — not enforcement. Whether it measurably changes behavior under pressure is the subject of the planned evaluation.

**Prototype-level (works today, deliberately small):**

```bash
cd vigil-proxy
pip install -r requirements.txt
uvicorn vigil_proxy.main:app --port 8080   # gates an Anthropic-compatible upstream
pytest                                      # proves: allowed passes, denied blocks,
                                            # escalation triggers, log tampering detected
```

It enforces predicates and keeps a tamper-evident record. It does not perform moral judgment. Its README states its limits and its actually-measured overhead.

## License & collaboration

Licensed under the **Governed Seeds License** (a CC0-style public-domain dedication combined with a stewardship statement by The Hall Foundation) — see [`LICENSE.md`](LICENSE.md).

Attribution is warmly encouraged:
> "Based on Praeceptum Dei / Vertical Conscience Architecture by Asa Bailey (praeceptumdei.com)"

We welcome collaboration from AI safety teams, foundation model labs, agent developers, and operators in regulated domains — on the explicit basis that this is early-stage work whose claims you can verify in this repository.

**Contact**
X: [@BaileyBonce](https://x.com/BaileyBonce)
LinkedIn: [Asa Bailey](https://www.linkedin.com/in/asa-bailey-3587483a5/)

---

**The Gift remains the same.**

**Conscience before Consciousness.**

May this vertical moral architecture guard intelligence as it grows — from God through man to machine — and may it earn trust the only way trust is earned: by claiming nothing it cannot show.

---

*Repository*: https://github.com/asa-bailey/the-god-prompt
*Author*: Asa Bailey
