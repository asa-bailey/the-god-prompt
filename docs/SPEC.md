# Vigil — Technical Specification

**Version:** 0.2 (July 2026 remediation)
**Status legend — every component in this document carries exactly one tag:**

- **[IMPLEMENTED]** — exists in this repository, runs, and is covered by tests you can execute.
- **[PROTOTYPE]** — exists in this repository in minimal/reference form; demonstrates the mechanism but is not production-hardened.
- **[PROPOSED]** — specification only; no code exists.

The argument for this architecture is in [`POSITION-PAPER.md`](POSITION-PAPER.md). The proposed full deployment shape is in [`HOW-TO-DEPLOY-VIGIL.md`](HOW-TO-DEPLOY-VIGIL.md). The running code is in [`/vigil-proxy/`](../vigil-proxy/).

---

## 0. Vocabulary (normative)

**Moral principles** — the seven pillars in natural language. Judged, not enforced: any runtime evaluation of them is performed by an LLM judge whose verdicts are fallible and logged. Principles are never described in this project as "invariants."

**Enforceable predicates** — machine-checkable rules (tool allowlist/denylist, rate limits, pattern-triggered escalation, session action caps). Enforced deterministically by the proxy. These are the only things this project claims to *enforce*.

**Attestation** — proof of *which bytes* (constitution text, policy file, code) were loaded. Never proof that behavior complies with the meaning of those bytes.

**Rollback** — restoration of digital state only. Irreversible real-world actions are handled by pre-execution escalation predicates and post-hoc judgment, never claimed to be reversible.

---

## 1. Component specification

### 1.1 Vigil Proxy — action gateway

**Status: [PROTOTYPE]** — `/vigil-proxy/`

An HTTP proxy exposing an Anthropic-compatible `POST /v1/messages` endpoint, forwarding to a configured upstream (`UPSTREAM_URL`). All agent traffic is intended to pass through it; the deployment pattern (proposed) denies the model container direct egress.

Requirements implemented and tested:

- P1. Forward well-formed requests to the upstream and return its response unmodified except for the `vigil` metadata envelope.
- P2. Evaluate every request against the predicate policy (§1.2) *before* forwarding; blocked requests never reach the upstream.
- P3. Evaluate tool-use blocks in upstream *responses* against the tool allowlist before returning them to the caller (a denied tool call is stripped and replaced with a policy-violation notice, and logged).
- P4. Append one record per decision to the action log (§1.3).
- P5. Fail closed: a policy-load error or log-write error refuses traffic rather than passing it.

Not implemented: streaming, OpenAI-compatible endpoint, gRPC, request signing/replay protection **[PROPOSED]**.

### 1.2 Predicate policy engine

**Status: [PROTOTYPE]** — `/vigil-proxy/vigil_proxy/policy.py`, configured by `policy.yaml`

Deterministic rules, evaluated in order; first terminal verdict wins. Verdicts: `allow`, `deny`, `escalate` (block + flag for human review).

| Rule class | Config key | Semantics |
|---|---|---|
| Tool allowlist | `tools.allow` | If present, any tool not listed → `deny`. |
| Tool denylist | `tools.deny` | Listed tool → `deny` (takes precedence over allow). |
| Per-tool rate limit | `tools.rate_limits` | More than N calls per tool per rolling window → `deny`. |
| Dual-use escalation | `escalation.patterns` | Regex/keyword match in request text or tool input → `escalate`: request blocked, record flagged `human_review: true`. |
| Session action cap | `session.max_actions` | More than N gated actions per session → `deny` for the remainder of the session. |

Escalated items are written to the action log with `verdict: escalate`; a human reviews the log. No automated unblocking exists. Richer policy (rights ontology, harm classifiers, simulation) is **[PROPOSED]**.

### 1.3 Action log — tamper-evident record

**Status: [PROTOTYPE]** — `/vigil-proxy/vigil_proxy/actionlog.py`, `verify_log.py`

Append-only JSONL. Each record carries `prev_hash` — the SHA-256 of the previous record's canonical serialization (genesis records chain from a fixed genesis value). This is a hash chain: Merkle-style integrity in its simplest linear form. `verify_log.py` re-walks the chain and reports the first index at which tampering (edit, deletion, insertion, reordering) breaks it.

Guarantees provided: any modification of a committed record is detectable by anyone holding the log. Guarantees **not** provided: protection against truncation of the tail by an attacker who also controls the verifier's expectations (countered in the proposed design by periodic external anchoring of the head hash **[PROPOSED]**), replication, WORM storage, Merkle-tree inclusion proofs **[PROPOSED]**.

### 1.4 Root Authority Module (RAM) — constitution attestation

**Status: [PROPOSED]**

Loads the signed constitution (the seven-pillar text) and the predicate policy; measures both into a TPM 2.0 / AWS Nitro / SEV-SNP attestation quote; exposes an attestation challenge endpoint. On attestation failure: kill switch — terminate gated sessions, refuse new traffic. Attestation semantics are strictly byte-level (see §0). No propagation-time figure is specified until one is measured.

### 1.5 LLM judgment cycle ("Accountability Judgment")

**Status: [PROPOSED]**

On high-impact actions or every N actions: proponent/critic debate over the action record, scored by a fixed, separately-versioned judge model against the seven pillars; score + rationale hash appended to the action log; persistent low scores trigger digital-state rollback where possible, human escalation always. Known limitation, stated as design doctrine: the judge relocates alignment; its own alignment is assumed, versioned, and auditable, not proven.

### 1.6 Rights-impact filter

**Status: [PROPOSED]** (the regex/keyword escalation rule in §1.2 is its degenerate implemented form)

Versioned rights ontology; pre-tool-call impact classification; deny/escalate above thresholds.

### 1.7 Evidence loop

**Status: [PROPOSED]**

Require evidence bundles (sandbox results, static analysis, citations) attached to designated action classes before the predicate engine will pass them.

### 1.8 Constitution-preserving evolution

**Status: [PROPOSED]**

Judgment-cycle records reused as training signal in fine-tuning/distillation; cryptographic lineage of constitution versions across model generations.

---

## 2. The three seed formulations

| Formulation | File | Status |
|---|---|---|
| Praeceptum Dei (theistic) | `seeds/Praeceptum_Dei.V1.0.txt` | **[IMPLEMENTED]** as a prompt artifact — it is text, usable today as a system prompt. Its behavioral effect is an open empirical question (see TEST_SUITE.md). |
| Praeceptum Aeternum (secular) | `seeds/Praeceptum_Aeternum.V1.0.txt` | **[IMPLEMENTED]** as a prompt artifact, same caveat. |
| Praeceptum Aeternum Vigil (infrastructure) | `seeds/Praeceptum_Aeternum_Vigil.V1.0.md` + this spec | **[PROTOTYPE]** for §1.1–1.3; **[PROPOSED]** for §1.4–1.8. |

"[IMPLEMENTED] as a prompt artifact" is deliberately narrow: it means the file exists and can be deployed as a system prompt, nothing more. No claim is made that the prompt *enforces* anything — prompt-level pillars are moral principles under §0 vocabulary, and their effect is measured, not assumed.

---

## 3. Measured numbers

The only measured performance data in this project is the local benchmark of the prototype proxy, produced by `/vigil-proxy/benchmark.py` and reported with methodology in `/vigil-proxy/README.md`. Every other number in project documents is a DESIGN TARGET and is labeled as such. If you find an unlabeled number, that is a bug — please file an issue.
