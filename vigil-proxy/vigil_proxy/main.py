"""FastAPI adapter for the Vigil gateway (requires: fastapi, httpx, uvicorn).

Run:  uvicorn vigil_proxy.main:app --port 8080
Env:  UPSTREAM_URL (default https://api.anthropic.com), VIGIL_POLICY, VIGIL_LOG

All enforcement logic lives in ``gateway.py`` (framework-free); this module
only translates HTTP <-> gateway calls. A zero-dependency alternative adapter
is ``stdlib_server.py``.
"""

from __future__ import annotations

import json
import os
from typing import Dict, Optional, Tuple

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .actionlog import ActionLog
from .gateway import Gateway, UpstreamError
from .policy import PolicyEngine, PolicyError

DEFAULT_UPSTREAM = "https://api.anthropic.com"
_FORWARD_HEADERS = ("x-api-key", "authorization", "anthropic-version", "content-type")


def create_app(
    policy_path: Optional[str] = None,
    log_path: Optional[str] = None,
    upstream_url: Optional[str] = None,
    transport: Optional[httpx.BaseTransport] = None,
) -> FastAPI:
    """App factory. ``transport`` is injectable so tests can mock the upstream."""
    policy_path = policy_path or os.getenv(
        "VIGIL_POLICY", os.path.join(os.path.dirname(__file__), "..", "policy.yaml"))
    log_path = log_path or os.getenv("VIGIL_LOG", "vigil_actions.jsonl")
    upstream = (upstream_url or os.getenv("UPSTREAM_URL", DEFAULT_UPSTREAM)).rstrip("/")

    app = FastAPI(title="Vigil Proxy (reference prototype)", version="0.1.0")

    # Fail closed on startup problems: record the error, refuse all traffic.
    startup_error: Optional[str] = None
    gateway: Optional[Gateway] = None
    client = httpx.Client(transport=transport, timeout=120.0)

    def upstream_call(body: dict, headers: Dict[str, str]) -> Tuple[int, dict]:
        try:
            resp = client.post(f"{upstream}/v1/messages", json=body, headers=headers)
            return resp.status_code, resp.json()
        except (httpx.HTTPError, json.JSONDecodeError) as e:
            raise UpstreamError(str(e)) from e

    try:
        gateway = Gateway(PolicyEngine.from_file(policy_path), ActionLog(log_path), upstream_call)
    except (PolicyError, OSError) as e:
        startup_error = str(e)

    @app.post("/v1/messages")
    async def messages(request: Request) -> JSONResponse:
        if startup_error is not None:
            return JSONResponse(
                {"type": "error",
                 "error": {"type": "vigil_unavailable", "message": f"fail-closed: {startup_error}"}},
                status_code=503)
        try:
            body = await request.json()
        except json.JSONDecodeError:
            return JSONResponse(
                {"type": "error",
                 "error": {"type": "invalid_request_error", "message": "body is not valid JSON"}},
                status_code=400)
        session = request.headers.get("x-vigil-session", "default")
        headers = {k: v for k, v in request.headers.items() if k.lower() in _FORWARD_HEADERS}
        status, data = gateway.handle_messages(body, session, headers)
        return JSONResponse(data, status_code=status)

    @app.get("/health")
    async def health() -> dict:
        if startup_error is not None:
            return {"status": "fail-closed", "error": startup_error}
        return {"status": "ok", "version": "0.1.0", "enforced": "predicates-only"}

    return app


app = create_app()
