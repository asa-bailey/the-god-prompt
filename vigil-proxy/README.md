# vigil-proxy — Reference Prototype (v0.1.0)

The one part of the Vigil architecture that exists as running, tested code.
Deliberately small. Deliberately honest.

## What it is

An Anthropic-compatible `POST /v1/messages` proxy that forwards to a configured
upstream and enforces **machine-checkable predicates** on the way through:

- **Tool allowlist / denylist** — tools declared in requests and `tool_use`
  blocks in responses are checked; denied calls never execute (request-side
  blocks never reach the upstream; response-side blocks are stripped, replaced
  with a policy notice, and logged).
- **Per-tool rate limits** — rolling window, per session.
- **Dual-use escalation** — regex/keyword patterns over request text and tool
  inputs; a match **blocks and flags for human review** (`human_review: true`
  in the log). There is no automated unblocking.
- **Max actions per session** — hard cap.
- **Tamper-evident action log** — append-only JSONL where every record carries
  the SHA-256 of the previous record (hash chain). `verify_log.py` detects any
  edit, deletion, insertion, or reordering of committed records.
- **Fail closed** — bad policy file or failed log write ⇒ traffic refused (503).

## What it is NOT

Read this list as carefully as the one above:

- It performs **no moral judgment**. A regex match is not an ethical finding.
- It does **not implement the seven pillars**. The pillars are natural-language
  moral principles; evaluating them requires an LLM judge, which is
  [PROPOSED, not implemented] — and which would relocate rather than solve
  alignment (see `docs/POSITION-PAPER.md`).
- It does **no semantic analysis** of any kind. A request that avoids the
  configured patterns passes. Predicate floors are routable-around by design
  pressure; that is why they are a *floor*, not a safety argument.
- It does **not do attestation**, debate cycles, rights ontologies, Merkle-tree
  ledgers, or anything else tagged [PROPOSED] in `docs/SPEC.md`.
- The hash chain does **not** protect against truncation of the log tail by an
  attacker who also controls the verifier's expectations (external anchoring of
  the head hash is the proposed mitigation — not implemented).

## Layout

```
vigil-proxy/
├── policy.yaml              # example predicate policy
├── verify_log.py            # detects log tampering (exit 1 on tamper)
├── benchmark.py             # measures real overhead on YOUR machine
├── requirements.txt         # fastapi/uvicorn/httpx only needed for the FastAPI adapter
├── vigil_proxy/
│   ├── gateway.py           # ALL enforcement logic (framework-free; needs only PyYAML)
│   ├── policy.py            # predicate engine
│   ├── actionlog.py         # hash-chained JSONL log
│   ├── main.py              # FastAPI adapter
│   └── stdlib_server.py     # zero-dependency http.server adapter
└── tests/test_proxy.py      # the proof of the four claims
```

## Run it

FastAPI adapter (recommended):

```bash
pip install -r requirements.txt
UPSTREAM_URL=https://api.anthropic.com uvicorn vigil_proxy.main:app --port 8080
```

Zero-dependency adapter (stdlib + PyYAML only — same enforcement logic):

```bash
python -m vigil_proxy.stdlib_server --port 8080 --upstream https://api.anthropic.com
```

Then point any Anthropic SDK/client at `http://localhost:8080` (auth headers
are passed through). Per-session predicates key off the `x-vigil-session` header.

## Test it

```bash
pytest tests/            # or, with zero extra deps:
python -m unittest discover -s tests
```

The suite proves exactly four claims: allowed calls pass; denied calls are
blocked (denylist, allowlist, rate limit, session cap — and blocked requests
never reach the upstream); escalations trigger with the human-review flag; and
log tampering (edit / delete / reorder) is detected. 18 tests; the 2
FastAPI-adapter tests skip automatically if fastapi isn't installed.

Verify a log:

```bash
python verify_log.py vigil_actions.jsonl   # exit 0 = chain intact, 1 = tampered
```

## Measured overhead

From `benchmark.py` (500 sequential requests, zero-latency in-process mock
upstream, so this is the proxy's own work only — predicates + fsync'd log
append, plus localhost HTTP for the end-to-end row):

```
Environment: Linux 6.8 VM, 2 vCPU (i9-13950HX host), Python 3.10.12 — 2026-07-16

gateway core: text-only request               n=500  p50=  1.375 ms  p99=  1.868 ms
gateway core: gated tool_use response         n=500  p50=  2.628 ms  p99=  4.144 ms
end-to-end: stdlib HTTP adapter (localhost)   n=500  p50=  1.907 ms  p99=  3.742 ms
```

Honest caveats: single sequential client; no network/TLS; no real model
upstream (real upstream latency dwarfs these numbers); every log append calls
`fsync`, which dominates the cost; a shared-hardware VM, so treat these as
indicative. Run `python benchmark.py` yourself — the README number that
matters is the one from your machine.

## Relation to the rest of the project

This prototype is the [PROTOTYPE]-tagged subset of `docs/SPEC.md` (§1.1–1.3).
The argument for why a predicate floor at the action boundary is worth having
at all is `docs/POSITION-PAPER.md`. Everything grander that earlier project
material described — attestation, judges, ledgers, kill switches — remains
[PROPOSED] and is labeled that way wherever it is mentioned.
