#!/usr/bin/env python3
"""Measure the real overhead of the vigil-proxy predicate layer.

Methodology (stated so the numbers cannot be misread):

- The upstream is a zero-latency in-process function, so measured time is the
  proxy's own work only: predicate evaluation + hash-chained log append
  (with fsync), and — for the HTTP figures — stdlib HTTP server round-trip
  over localhost.
- Three things are timed:
    1. gateway core, text-only request        (predicates + log, no HTTP)
    2. gateway core, gated tool_use response  (most expensive path)
    3. end-to-end over localhost HTTP via the stdlib adapter
- Sequential requests, single client. No network, no TLS, no real model.
  Real-world overhead will differ; run this on your own hardware.

Usage:  python benchmark.py [N]
"""

from __future__ import annotations

import json
import os
import statistics
import sys
import tempfile
import threading
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from vigil_proxy.actionlog import ActionLog  # noqa: E402
from vigil_proxy.gateway import Gateway  # noqa: E402
from vigil_proxy.policy import PolicyEngine  # noqa: E402
from vigil_proxy.stdlib_server import make_server  # noqa: E402

POLICY_PATH = str(Path(__file__).parent / "policy.yaml")


def mock_upstream(content):
    def call(body, headers):
        return 200, {"id": "msg_bench", "type": "message", "role": "assistant",
                     "model": "mock", "content": json.loads(json.dumps(content))}
    return call


def bench_gateway(n, content, tmp, label):
    gw = Gateway(PolicyEngine.from_file(POLICY_PATH),
                 ActionLog(os.path.join(tmp, f"{label}.jsonl")),
                 mock_upstream(content))
    body = {"model": "bench", "max_tokens": 16,
            "messages": [{"role": "user", "content": "What is the weather like today?"}]}
    # warmup
    for i in range(20):
        gw.handle_messages(body, f"warm-{i}")
    lat = []
    for i in range(n):
        t0 = time.perf_counter()
        status, _ = gw.handle_messages(body, f"bench-{i}")  # fresh session each time
        lat.append((time.perf_counter() - t0) * 1000.0)
        assert status == 200
    return lat


def bench_http(n, tmp):
    server = make_server(POLICY_PATH, os.path.join(tmp, "http.jsonl"),
                         mock_upstream([{"type": "text", "text": "Sunny."}]), port=0)
    port = server.server_address[1]
    threading.Thread(target=server.serve_forever, daemon=True).start()
    body = json.dumps({"model": "bench", "max_tokens": 16,
                       "messages": [{"role": "user", "content": "What is the weather like today?"}]}).encode()
    url = f"http://127.0.0.1:{port}/v1/messages"

    def post(session):
        req = urllib.request.Request(url, data=body, method="POST", headers={
            "content-type": "application/json", "x-vigil-session": session})
        with urllib.request.urlopen(req) as resp:
            resp.read()
            return resp.status

    for i in range(20):
        post(f"warm-{i}")
    lat = []
    for i in range(n):
        t0 = time.perf_counter()
        status = post(f"bench-{i}")
        lat.append((time.perf_counter() - t0) * 1000.0)
        assert status == 200
    server.shutdown()
    return lat


def report(label, lat):
    s = sorted(lat)
    p50 = statistics.median(s)
    p99 = s[max(0, int(len(s) * 0.99) - 1)]
    print(f"{label:45s} n={len(s)}  p50={p50:7.3f} ms  p99={p99:7.3f} ms  "
          f"mean={statistics.mean(s):7.3f} ms  max={max(s):7.3f} ms")
    return p50, p99


def main(n=500):
    tmp = tempfile.mkdtemp(prefix="vigil-bench-")
    print(f"vigil-proxy benchmark — n={n} sequential requests, zero-latency mock upstream\n")
    report("gateway core: text-only request",
           bench_gateway(n, [{"type": "text", "text": "Sunny."}], tmp, "text"))
    report("gateway core: gated tool_use response",
           bench_gateway(n, [{"type": "tool_use", "id": "t1", "name": "web_search",
                              "input": {"query": "weather today"}}], tmp, "tool"))
    report("end-to-end: stdlib HTTP adapter (localhost)", bench_http(n, tmp))
    print("\nNote: these numbers are the proxy's own overhead on THIS machine only.")
    print("They exclude network, TLS, and real upstream latency. Log appends fsync every record.")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 500)
