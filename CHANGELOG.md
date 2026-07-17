# Changelog

## 2026-07-16 — Credibility & Architecture Remediation

### Why

This project's target audience — alignment researchers, safety teams, regulated
deployers — is precisely the audience most practiced at detecting unsupported
claims. Fabricated evidence does not merely fail to persuade them; it
disqualifies the work, including the parts that are sound. Prior to this
remediation the repository contained benchmark figures that were never measured,
red-team results from an exercise that never occurred, container images and Helm
repositories that were never published, institutional relationships that did not
exist, a placeholder checksum (the SHA-256 of the empty string) presented as
document control, and a "verification hash" that does not match the file it
claims to verify. Every one of those, if checked, collapses — and this audience
checks. The philosophy (seven pillars, conscience before consciousness, vertical
enforcement) deserved better than to be discredited by its packaging.

The governing rule going forward: every claim is (a) implemented and verifiable
in this repo, (b) labeled **DESIGN TARGET — not yet measured**, or (c) labeled
**PROPOSED — not yet implemented**.

### Phase 1 — Fabricated evidence removed (commit `c995d70`)

- `docs/HOW-TO-DEPLOY-VIGIL.md` retitled **"Vigil v1.0 — Proposed Deployment
  Architecture (Specification, Unimplemented)"**. Removed or relabeled as design
  targets: P50 87 ms / P99 172 ms latency figures, 18–24% token overhead,
  9–14 GB GPU memory, the 47 ms kill-switch claim, and the "14,872 adversarial
  prompts / Q1 2026 red team" results (no such exercise took place).
- Removed references to infrastructure that does not exist: the
  `charts.praeceptumdei.com` Helm repo, `vigil/proxy:1.0.1` / `vigil/ledger` /
  `vigil/judge` container images, the separate `asa-bailey/vigil` repository,
  the Matrix channel, the `vigil-judge-34b` model, "Big Four" audit
  relationships, and the `training/` directory.
- Replaced the empty-string SHA-256 placeholder with a checksum-at-release note.
- Archived (not deleted) the mock `vigil/` code — which returned hard-coded
  pillar scores and a fake attestation hash — and the deploy configs, to
  `docs/archive/`.
- Corrected `docs/Post-Colossus-Test-Architecture-Evolution.md` and
  `docs/TESTRESULTS_...md`: the Grok X-thread exchanges exercised no running
  enforcement layer; the "Vatican Ethics Committee / NVIDIA" distribution line
  named relationships that did not exist.

### Phase 2 — Vision split from specification (commit `aa020ff`)

- Added `docs/POSITION-PAPER.md`: the argument for vertical runtime enforcement,
  situated against AI Control (Greenblatt et al., Redwood Research),
  Constitutional AI (Bai et al., Anthropic), Guaranteed Safe AI (Dalrymple et
  al.), and OS-level sandboxing / remote-attestation literature — stating what
  Vigil adds and what it inherits. No implementation claims.
- Added `docs/SPEC.md`: every component tagged [IMPLEMENTED] / [PROTOTYPE] /
  [PROPOSED], with normative vocabulary.
- `README.md` slimmed into an honest front door with a project-status line and
  exists-vs-proposed tables; license reference corrected to the Governed Seeds
  License actually in `LICENSE.md`.

### Phase 3 — Conceptual language corrected (commit `5e4d750`)

- The seven pillars are no longer called "invariants." **Moral principles**
  (natural language, judged by an LLM evaluator — which relocates rather than
  solves alignment) are now distinguished everywhere from **enforceable
  predicates** (machine-checkable rules the proxy can actually enforce).
- Attestation language corrected: hardware attestation proves which constitution
  text and code were loaded (bytes), not that behavior complies with their
  meaning (semantics).
- "Executed before consciousness" reworded wherever it described the proxy: a
  wrapper gates actions (inputs, outputs, tool calls); it cannot precede or
  inspect the model's internal computation. The slogan survives as an ordering
  of constraints-before-action.
- Rollback claims constrained to digital state; irreversible real-world actions
  are handled post-hoc (detect, log, escalate, halt).
- The theistic root authority reframed as an empirical hypothesis about framing
  effects, with a proposed ablation design added to `TEST_SUITE.md`.
- Verbatim artifacts (Grok's open letter, the X transcript) preserved untouched,
  with editorial prefaces stating what they are and are not.

### Phase 4 — A real reference implementation (commit `9cabb78`)

- Added `/vigil-proxy/`: Anthropic-compatible proxy enforcing predicate policy
  from `policy.yaml` (tool allow/denylist, per-tool rate limits, regex dual-use
  escalation with human-review flagging, session action caps), with a
  hash-chained append-only action log, `verify_log.py` tamper detection, an
  18-test suite (all passing), and a benchmark script that was actually run —
  its real numbers, environment, and caveats are in `vigil-proxy/README.md`.
- Its README states plainly what the prototype does NOT do: moral judgment,
  alignment, semantics.

### Phase 5 — Evaluation plan and this changelog

- `TEST_SUITE.md` rewritten as a real evaluation plan: pre-registered framing
  ablation for the seeds (transcendent vs. secular vs. content-only vs.
  baseline), and integration tests for the proxy that exist and can be
  referenced honestly. During this rewrite the claimed "SHA-256 provided by
  @grok" was checked against the transcript file across the full git history:
  **it does not match at any revision** and the "cryptographic verification"
  claim has been withdrawn.
- Original documents preserved in `docs/archive/` with an explanatory index.

### Not changed

- The seven pillars, the three seed prompts, the project's voice and mission.
- The whitepaper PDF (binary, as circulated) — the companion
  `docs/WHITEPAPER.V2.0.md` carries the corrections and a terminology note.
- Git history: nothing was rewritten; the record of what was claimed stands.
