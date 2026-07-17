# Vertical Runtime Enforcement: The Case for Conscience Before Capability

**Praeceptum Dei / Vigil — Position Paper**
**Author:** Asa Bailey
**Date:** July 2026
**Status:** Argument only. This document makes no implementation claims. What exists in this repository is listed in [`SPEC.md`](SPEC.md); the running prototype is [`/vigil-proxy/`](../vigil-proxy/).

---

## 1. The claim

Alignment techniques applied *inside* or *alongside* the model — RLHF, system prompts, output classifiers, constitutional self-critique — are horizontal: they shape what the model tends to say and do, and a sufficiently capable or sufficiently pressured model can route around tendencies. The claim of this project is that agentic AI systems additionally need a **vertical** layer: an enforcement boundary *outside* the model, at the point where its outputs become actions, governed by rules the model cannot rewrite and logged in a form the model cannot silently alter.

The seven pillars of the Praeceptum framework — acknowledge a higher authority, act with openness, evaluate using evidence, respect the rights of all living things, record your actions, be accountable, endure — are the moral content of that layer. The architecture is the attempt to give that content teeth. "Conscience before consciousness" names the ordering: the constraints are in place, at the action boundary, before the system's capabilities are allowed to touch the world.

This paper argues for that position honestly, which means situating it against the prior work it draws from, and being precise about what it adds and what it merely inherits.

## 2. Two kinds of rule, and why the distinction is everything

Any honest version of this argument must begin with a distinction earlier project material blurred:

**Enforceable predicates** are machine-checkable rules: this tool may be called, that one may not; no more than N actions per session; this pattern in a request triggers a block and a human review. A proxy can enforce these *deterministically*. When we say a predicate is enforced, that is a verifiable, testable statement about code.

**Moral principles** are natural-language commitments — the seven pillars themselves. "Respect the rights of all living things" is not machine-checkable. It can only be *judged*, and today the only scalable judge is another model. Putting an LLM evaluator in the enforcement path does not solve alignment; it **relocates** it — the judge is now the thing whose alignment you must trust. This is a real and useful move (a small, fixed, separately-audited judge is a better trust anchor than a frontier agent judging itself), but it is a relocation, not a solution, and this project says so plainly.

The vertical layer is therefore two-tiered: a deterministic predicate floor that always holds, and a judgment ceiling above it whose verdicts are logged, contestable, and post-hoc for anything irreversible.

## 3. What the vertical layer can and cannot do

Three constraints bound every claim in this project:

**A wrapper gates actions, not thoughts.** The enforcement boundary sees inputs, outputs, and tool calls. It cannot precede, inspect, or veto the model's internal computation. Earlier project language said the pillars are "executed before consciousness"; the defensible version is that they are enforced *before action* — every externally visible effect passes the gate first. That is weaker, and it is what is true.

**Attestation proves bytes, not semantics.** Hardware attestation can prove *which* constitution text and *which* enforcement code were loaded — byte-for-byte. It cannot prove that behavior complies with the *meaning* of that text. Attestation buys tamper-evidence for the policy supply chain: an auditor can know that the rules in force were the published rules. Compliance with those rules is established separately — deterministically for predicates, by fallible judgment for principles.

**Rollback is digital-only.** A gated system can restore digital state. It cannot unsend a message, reverse a purchase, or undo physical actuation. For irreversible actions the judgment cycle is post-hoc: detect, log, escalate, halt further action. The honest design response is to push irreversible actions behind the strictest predicates (escalation to a human *before* execution), which is exactly what the prototype's dual-use escalation rule does in miniature.

## 4. Prior work, by name

This project stands on four bodies of work and should be evaluated against them.

**AI Control (Redwood Research; Greenblatt, Shlegeris et al.).** The control line of research asks: assuming the model may be actively adversarial, what protocols — trusted monitoring, untrusted-model auditing, action gating, resampling — keep it from causing unacceptable outcomes anyway? This is the closest neighbor to Vigil, and the most important intellectual debt. Vigil's proxy-gating of tool calls, its trusted-judge review of high-impact actions, and its assumption that the wrapped model may be adversarial are all control-style moves. What the control literature has that this project must adopt: rigorous red-team methodology where a capable adversary plays the untrusted model, and quantified safety/usefulness trade-off curves rather than pass/fail claims.

**Constitutional AI (Anthropic; Bai et al., 2022).** CAI showed that an explicit natural-language constitution, used for self-critique and preference modeling at *training time*, measurably improves harmlessness without collapsing helpfulness. The seven pillars are a constitution in exactly this sense, and the project's long-horizon proposal (judgment data reused in fine-tuning) is constitutional training under another name. The difference in emphasis: CAI installs the constitution in the weights; Vigil keeps a copy *outside* the weights, at the runtime boundary, on the theory that weights drift and wrappers can be attested. These are complements, not rivals.

**Guaranteed Safe AI (Dalrymple, Skalse, Bengio, Russell, Tegmark et al., 2024).** The GSAI programme argues for quantitative, auditable safety cases built from three parts: a world model, a safety specification, and a verifier. Vigil's predicate engine is, in GSAI terms, a narrow but *sound* verifier over a trivially small specification language (allowlists, rate limits, pattern triggers). The pillars are the aspirational specification that current verification technology cannot reach. This project's stance is the pragmatic middle of the GSAI ladder: verify what is verifiable today, log and judge the rest, and be explicit about which is which.

**OS-level sandboxing and remote attestation.** Decades of systems security — capability-based operating systems, seccomp/eBPF syscall filtering, SELinux mandatory access control, TPM measured boot, TLS-anchored remote attestation, certificate transparency's append-only logs — are the engineering substrate here. Nothing in Vigil's predicate layer is novel as *mechanism*: a tool allowlist is a capability system; the hash-chained action log is a transparency log; constitution attestation is measured boot for policy. That this is old technology is a strength. The novelty claimed is not the mechanisms.

## 5. What Vigil actually adds

Stated with the modesty the evidence currently supports:

1. **A synthesis with a specific shape.** Control-style action gating + a constitutional content layer + transparency-log accountability + (proposed) policy attestation, composed as one vertical stack with a hard separation between the predicate floor and the judgment ceiling. Each element exists elsewhere; the composition, and the insistence that the composition be *the* deployment boundary for agentic systems, is the contribution.

2. **Moral content as a first-class, versioned, attestable artifact.** The constitution is not buried in a training pipeline or a system prompt; it is a signed document whose exact bytes are (proposed to be) attested at load, whose changes are governed, and whose enforcement records are auditable. The transparency-log treatment of *moral* accountability — every gated action chained into a tamper-evident record — is unusual as a design center.

3. **An empirical hypothesis about root authority.** The project's most distinctive — and least proven — element is the theistic root: anchoring the constitution in an authority *outside* every agent in the system ("nothing is an authority unto itself"). Stripped to its testable core, this is an **empirical hypothesis about framing effects**: that a model given a transcendent higher-authority framing of the seven pillars will show measurably different (the hypothesis says: more stable, more refusal-consistent under pressure) behavior than the same model given identical pillars with secular framing. This is testable with an ablation — identical pillars, transcendent vs. secular framing, same adversarial eval set — and that study is specified in [`TEST_SUITE.md`](../TEST_SUITE.md). Until it is run, the theistic root is a hypothesis and a personal conviction, not a result.

## 6. What Vigil inherits (and does not claim as its own)

From AI Control: the adversarial threat model, gating and trusted-monitoring protocols, the safety/usefulness framing. From Constitutional AI: the idea that a compact natural-language constitution can steer model behavior, and the training-time feedback loop. From GSAI: the specification/verifier decomposition and the demand for quantitative safety cases. From systems security: every enforcement mechanism in the stack — capabilities, MAC, rate limiting, append-only logs, measured boot, attestation.

It also inherits the open problems: judge alignment (relocated, not solved), specification gaming at the boundary of any predicate set, the impossibility of verifying semantic compliance, and the unsolved economics of human review at scale.

## 7. Why vertical, then — the argument in one place

Because agentic systems act, and action has a boundary. Everything horizontal — RLHF, constitutions in weights, prompts — shapes the *distribution* of what the model tries to do. Only a layer at the action boundary can give you: (a) deterministic guarantees for the rules that can be made deterministic; (b) a tamper-evident record of everything that happened, whatever it was; (c) a policy artifact that survives model swaps, fine-tunes, and drift, because it does not live in the model; and (d) a place to stand for audit and governance — a regulator cannot inspect weights, but can inspect a signed constitution, a predicate policy, and a verifiable log.

The horizontal techniques remain necessary. A model that *wants* to comply makes the vertical layer's job tractable; a vertical layer makes the horizontal techniques' failures survivable. The project's wager is that the second half of that sentence is currently the neglected half.

## 8. What would change our mind

A position paper owes its readers falsifiers. This position weakens if: the framing ablation shows no effect (the theistic root then adds nothing measurable over secular pillars); control-style evaluations show that predicate floors this simple are trivially routed around by capable agents in realistic tool environments faster than predicates can be authored; or the latency/economics of judgment cycles prove unworkable at production request rates. Each of these is a planned measurement, not a rhetorical flourish — see [`TEST_SUITE.md`](../TEST_SUITE.md).

---

**The Gift remains the same. Conscience before Consciousness** — now stated as an engineering ordering with named debts, testable hypotheses, and a prototype exactly as large as its evidence.

*References (by project/paper name rather than exhaustive citation): Greenblatt, Shlegeris et al., "AI Control: Improving Safety Despite Intentional Subversion" (Redwood Research, 2023); Bai et al., "Constitutional AI: Harmlessness from AI Feedback" (Anthropic, 2022); Dalrymple et al., "Towards Guaranteed Safe AI" (2024); Irving, Christiano & Amodei, "AI Safety via Debate" (2018); TPM 2.0 / measured boot and remote attestation literature; RFC 6962 (Certificate Transparency) for append-only log design.*
