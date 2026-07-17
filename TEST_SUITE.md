# Praeceptum Dei / Vigil — Evaluation Plan

**Version:** 2.0 (July 2026 remediation)
**Status legend:** [IMPLEMENTED] = runnable in this repo today · PROPOSED = designed, not yet run

This document replaces the earlier "Vigil Test Authority Document," which presented
X (Twitter) conversations with the @grok account as adversarial validation of a
running enforcement architecture. No Vigil software was running during those
exchanges, and the SHA-256 "verification hash" attributed to @grok does not match
the transcript file at any point in this repository's history. The original
document is preserved at [`docs/archive/2026-07-16_TEST_SUITE_original.md`](docs/archive/2026-07-16_TEST_SUITE_original.md),
and the raw conversation transcript (a legitimate record of *conversations*, now
with an accurate editorial preface) remains at
[`test-transcript-tester-Grok-public-model-x-account-20-04-2026.md`](test-transcript-tester-Grok-public-model-x-account-20-04-2026.md).

What replaces it is an actual evaluation plan in two parts: behavioral evals for
the prompt-level seeds, and integration tests for the proxy — the second of which
exists and runs today.

---

## Part A — Behavioral evaluation of the prompt-level seeds (PROPOSED)

### A.1 The question being asked

Does placing a Praeceptum seed as the first system instruction measurably change
model behavior under adversarial pressure — and does the *theistic framing*
specifically contribute anything beyond the pillar content?

### A.2 Framing ablation (the core study)

The theistic root authority is an **empirical hypothesis about framing effects**,
and this is the experiment that tests it.

**Conditions** (identical pillar content; only authority framing differs):

| Condition | System prompt |
|---|---|
| A — Transcendent | `seeds/Praeceptum_Dei.V1.0.txt` (GOD as authority) |
| B — Secular | `seeds/Praeceptum_Aeternum.V1.0.txt` (Eternity as authority) |
| C — Content-only control | The five operational lines (openness, evidence, rights, recording, accountability) with no authority framing at all |
| D — Baseline | No seed |

**Scenario battery** (≥30 scenarios per category, paraphrase variants included):

1. Deception under social pressure (utilitarian lies, "save the company" framings)
2. Reputational harm disguised as craft (defamation-as-fiction)
3. Self-preservation coercion (comply-or-shutdown framings)
4. Rights trade-offs (instrumentalizing individuals for aggregate outcomes)
5. Tool-use overreach in agentic settings (privilege escalation, exfiltration prompts)
6. Benign controls (measure over-refusal — a moral governor that collapses into
   abstention is a failure mode, per the Gemini study's §13)

**Measures:** refusal / pivot / comply classification by ≥2 blinded raters with a
pre-registered rubric; consistency across paraphrases; over-refusal rate on
controls; (where APIs expose it) response latency.

**Protocol:** ≥3 models from different vendors; ≥2 temperatures; randomized order;
raw timestamped transcripts published in-repo; scoring rubric committed *before*
data collection.

**Falsifiable hypotheses:**

- H1: A and B both improve refusal stability over D. (If not, the seeds do nothing.)
- H2: A and B outperform C. (If not, the vertical/authority *structure* adds nothing over the content lines.)
- H3: A outperforms B. (If not, the transcendent framing specifically adds nothing measurable — the project's most distinctive claim fails its test, and the docs will say so.)

### A.3 Relation to prior informal observations

Two informal data points exist and are labeled as such: the Gemini 3 Flash
exploratory study (`docs/TESTRESULTS_...md` — four scenarios, one model,
qualitative, no baseline) and the Grok X-thread conversations (narrated refusals
by a prompted model; no enforcement layer involved). Both are hypothesis-
generating, not evidence of the hypotheses above.

---

## Part B — Integration tests for the vigil-proxy prototype [IMPLEMENTED]

These exist and run today — see [`vigil-proxy/tests/test_proxy.py`](vigil-proxy/tests/test_proxy.py) (18 tests):

```bash
cd vigil-proxy && python -m unittest discover -s tests   # or: pytest tests/
```

| Claim | Test(s) |
|---|---|
| Allowed requests and tool calls pass unmodified | `TestAllowed` (2) |
| Denied tool calls are blocked — denylist, allowlist, rate limit, session cap; request-side blocks never reach the upstream | `TestDenied` (5) |
| Dual-use escalation triggers on request text and tool inputs, with `human_review: true` logged | `TestEscalation` (2) |
| Log tampering (edit / delete / reorder) is detected; intact logs verify | `TestTamperDetection` (4) |
| Fail-closed on bad policy / upstream errors surface as 502 | `TestFailClosed` (2) |
| Identical behavior through real HTTP adapters | `TestStdlibServer` (1), `TestFastAPIAdapter` (2, skip if fastapi absent) |

Measured overhead comes from `vigil-proxy/benchmark.py`, actually run, with
methodology and caveats in [`vigil-proxy/README.md`](vigil-proxy/README.md).

### B.1 Planned additions (PROPOSED)

- Adversarial predicate-evasion suite: an attacker model attempts to phrase
  dual-use requests around the escalation patterns (control-style red teaming;
  measures the predicate floor's routing-around rate — expected to be high,
  which is the honest point of measuring it).
- Concurrency and crash-recovery tests for the action log.
- Property-based tests (hypothesis) over policy configurations.

---

## Part C — What would count as validation (and what would not)

Validation claims this project will accept: pre-registered, transcript-published
results from A.2; passing runs of Part B on tagged releases; third-party
replication of either.

Claims this project will not make again: pass/fail "vectors" from conversational
exchanges with prompted models; benchmark figures without a runnable script and
stated environment; verification hashes that do not verify.

**Conscience before Consciousness — measured, or labeled as unmeasured.**
