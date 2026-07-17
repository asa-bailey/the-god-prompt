"""Zero-dependency adapter: the Vigil gateway on http.server (stdlib only).

Useful where FastAPI/httpx cannot be installed, and as the HTTP path for the
benchmark. Enforcement logic is identical to the FastAPI adapter — both call
the same ``Gateway``.

Run:  python -m vigil_proxy.stdlib_server --port 8080 --upstream https://api.anthropic.com
"""

from __future__ import annotations

import argparse
import json
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Dict, Optional, Tuple

from .actionlog import ActionLog
from .gateway import Gateway, UpstreamCall, UpstreamError
from .policy import PolicyEngine, PolicyError

_FORWARD_HEADERS = ("x-api-key", "authorization", "anthropic-version", "content-type")


def urllib_upstream(upstream_url: str) -> UpstreamCall:
    base = upstream_url.rstrip("/")

    def call(body: dict, headers: Dict[str, str]) -> Tuple[int, dict]:
        req = urllib.request.Request(
            f"{base}/v1/messages",
            data=json.dumps(body).encode("utf-8"),
            headers={"content-type": "application/json", **headers},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                return resp.status, json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            try:
                return e.code, json.loads(e.read().decode("utf-8"))
            except (json.JSONDecodeError, OSError):
                raise UpstreamError(f"upstream HTTP {e.code}") from e
        except (urllib.error.URLError, OSError, json.JSONDecodeError) as e:
            raise UpstreamError(str(e)) from e

    return call


def make_server(policy_path: str, log_path: str,
                upstream_call: UpstreamCall, port: int = 8080,
                host: str = "127.0.0.1") -> ThreadingHTTPServer:
    startup_error: Optional[str] = None
    gateway: Optional[Gateway] = None
    try:
        gateway = Gateway(PolicyEngine.from_file(policy_path), ActionLog(log_path), upstream_call)
    except (PolicyError, OSError) as e:
        startup_error = str(e)

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):  # keep stdout clean
            pass

        def _send(self, status: int, payload: dict) -> None:
            data = json.dumps(payload).encode("utf-8")
            self.send_response(status)
            self.send_header("content-type", "application/json")
            self.send_header("content-length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            if self.path == "/health":
                if startup_error is not None:
                    self._send(200, {"status": "fail-closed", "error": startup_error})
                else:
                    self._send(200, {"status": "ok", "version": "0.1.0",
                                     "enforced": "predicates-only"})
            else:
                self._send(404, {"type": "error", "error": {"type": "not_found", "message": self.path}})

        def do_POST(self):
            if self.path != "/v1/messages":
                self._send(404, {"type": "error", "error": {"type": "not_found", "message": self.path}})
                return
            if startup_error is not None:
                self._send(503, {"type": "error", "error": {
                    "type": "vigil_unavailable", "message": f"fail-closed: {startup_error}"}})
                return
            try:
                length = int(self.headers.get("content-length", 0))
                body = json.loads(self.rfile.read(length).decode("utf-8"))
            except (ValueError, json.JSONDecodeError):
                self._send(400, {"type": "error", "error": {
                    "type": "invalid_request_error", "message": "body is not valid JSON"}})
                return
            session = self.headers.get("x-vigil-session", "default")
            fwd = {k: v for k, v in self.headers.items() if k.lower() in _FORWARD_HEADERS}
            status, data = gateway.handle_messages(body, session, fwd)
            self._send(status, data)

    return ThreadingHTTPServer((host, port), Handler)


def main() -> None:
    ap = argparse.ArgumentParser(description="Vigil proxy (stdlib adapter)")
    ap.add_argument("--port", type=int, default=8080)
    ap.add_argument("--policy", default="policy.yaml")
    ap.add_argument("--log", default="vigil_actions.jsonl")
    ap.add_argument("--upstream", default="https://api.anthropic.com")
    args = ap.parse_args()
    server = make_server(args.policy, args.log, urllib_upstream(args.upstream), port=args.port)
    print(f"vigil-proxy (stdlib) listening on :{args.port} -> {args.upstream} (predicates-only)")
    server.serve_forever()


if __name__ == "__main__":
    main()
