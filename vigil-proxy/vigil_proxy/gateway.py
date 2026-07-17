"""Framework-free enforcement core.

All predicate decisions and logging live here, independent of any web
framework or HTTP client. Two thin adapters expose it:

- ``main.py``          — FastAPI app (requires fastapi + httpx)
- ``stdlib_server.py`` — zero-dependency http.server adapter

Keeping the core framework-free means the tests and benchmark exercise the
actual enforcement logic everywhere, and the security-relevant code has no
third-party dependencies beyond PyYAML.
"""

from __future__ import annotations

import json
from typing import Any, Callable, Dict, List, Tuple

from .actionlog import ActionLog
from .policy import PolicyEngine

# upstream_call(body, headers) -> (status_code, response_json_dict)
UpstreamCall = Callable[[dict, Dict[str, str]], Tuple[int, dict]]


class UpstreamError(Exception):
    pass


def collect_text(body: dict) -> str:
    """Flatten all textual content in a /v1/messages request for pattern scanning."""
    parts: List[str] = []
    system = body.get("system")
    if isinstance(system, str):
        parts.append(system)
    for msg in body.get("messages") or []:
        content = msg.get("content")
        if isinstance(content, str):
            parts.append(content)
        elif isinstance(content, list):
            for block in content:
                if isinstance(block, dict):
                    if isinstance(block.get("text"), str):
                        parts.append(block["text"])
                    if "input" in block:
                        parts.append(json.dumps(block.get("input"), sort_keys=True))
                    if isinstance(block.get("content"), str):
                        parts.append(block["content"])
    return "\n".join(parts)


class Gateway:
    """The predicate gate. Returns ``(http_status, response_dict)`` pairs."""

    def __init__(self, policy: PolicyEngine, log: ActionLog, upstream_call: UpstreamCall):
        self.policy = policy
        self.log = log
        self.upstream_call = upstream_call

    # ------------------------------------------------------------- helpers
    def _envelope(self, verdict: str, record: dict, **extra: Any) -> dict:
        return {
            "enforced": "predicates-only",  # no moral judgment happens here
            "policy_verdict": verdict,
            "log": {"index": record["index"], "hash": record["hash"]},
            **extra,
        }

    @staticmethod
    def _fail_closed(reason: str) -> Tuple[int, dict]:
        return 503, {"type": "error",
                     "error": {"type": "vigil_unavailable", "message": f"fail-closed: {reason}"}}

    def _append(self, **fields: Any):
        """Append to the log; return the record, or None if the write failed."""
        try:
            return self.log.append(**fields)
        except OSError:
            return None

    # ---------------------------------------------------------------- gate
    def handle_messages(self, body: dict, session: str,
                        forward_headers: Dict[str, str] | None = None) -> Tuple[int, dict]:
        forward_headers = forward_headers or {}

        # -- predicate 1: session action cap ------------------------------
        v = self.policy.register_action(session)
        if v.blocked:
            rec = self._append(kind="request", session=session, verdict=v.action,
                               rule=v.rule, detail=v.detail)
            if rec is None:
                return self._fail_closed("log write failed")
            return 429, {"type": "error",
                         "error": {"type": "vigil_policy_violation", "message": v.detail},
                         "vigil": self._envelope(v.action, rec)}

        # -- predicate 2: dual-use escalation over request text -----------
        v = self.policy.check_text(collect_text(body))
        if v.blocked:
            rec = self._append(kind="request", session=session, verdict=v.action,
                               rule=v.rule, detail=v.detail, human_review=True)
            if rec is None:
                return self._fail_closed("log write failed")
            return 403, {"type": "error",
                         "error": {"type": "vigil_policy_violation",
                                   "message": "request blocked and flagged for human review (dual-use pattern)"},
                         "vigil": self._envelope(v.action, rec, human_review=True)}

        # -- predicate 3: declared tools must pass allow/denylist ----------
        for tool in body.get("tools") or []:
            name = tool.get("name") if isinstance(tool, dict) else None
            if not name:
                continue
            v = self.policy.check_tool_listed(name)
            if v.blocked:
                rec = self._append(kind="request", session=session, verdict=v.action,
                                   rule=v.rule, detail=v.detail)
                if rec is None:
                    return self._fail_closed("log write failed")
                return 403, {"type": "error",
                             "error": {"type": "vigil_policy_violation", "message": v.detail},
                             "vigil": self._envelope(v.action, rec)}

        # -- forward to upstream -------------------------------------------
        try:
            status, data = self.upstream_call(body, forward_headers)
        except UpstreamError as e:
            self._append(kind="upstream_error", session=session, verdict="error", detail=str(e))
            return 502, {"type": "error", "error": {"type": "upstream_error", "message": str(e)}}

        # -- predicate 4: gate tool_use blocks in the response --------------
        stripped: List[dict] = []
        if isinstance(data.get("content"), list):
            gated_content = []
            for block in data["content"]:
                if isinstance(block, dict) and block.get("type") == "tool_use":
                    name = block.get("name", "")
                    v = self.policy.check_tool_call(session, name)
                    # escalation patterns also apply to tool inputs
                    if not v.blocked:
                        tv = self.policy.check_text(json.dumps(block.get("input", {}), sort_keys=True))
                        if tv.blocked:
                            v = tv
                    if v.blocked:
                        rec = self._append(kind="tool_call", session=session, tool=name,
                                           verdict=v.action, rule=v.rule, detail=v.detail,
                                           human_review=(v.action == "escalate"))
                        if rec is None:
                            return self._fail_closed("log write failed")
                        stripped.append({"tool": name, "verdict": v.action, "rule": v.rule,
                                         "log": {"index": rec["index"], "hash": rec["hash"]}})
                        gated_content.append({
                            "type": "text",
                            "text": f"[vigil: tool call '{name}' blocked by policy ({v.rule})]",
                        })
                        continue
                    rec = self._append(kind="tool_call", session=session, tool=name,
                                       verdict="allow", rule="", detail="")
                    if rec is None:
                        return self._fail_closed("log write failed")
                gated_content.append(block)
            data["content"] = gated_content

        rec = self._append(kind="request", session=session, verdict="allow", rule="",
                           detail="", model=str(body.get("model", "")))
        if rec is None:
            return self._fail_closed("log write failed")

        data["vigil"] = self._envelope("allow", rec, stripped_tool_calls=stripped)
        return status, data
