"""Enforceable-predicate policy engine.

Everything in this module is deterministic and machine-checkable. Verdicts:

- ``allow``    — the request/tool call proceeds
- ``deny``     — blocked outright (denylist, missing from allowlist, rate
                 limit exceeded, session cap exceeded)
- ``escalate`` — blocked AND flagged for human review (dual-use pattern match)

This engine performs no moral judgment. A pattern match is a pattern match;
whether the underlying request was actually dangerous is exactly the kind of
semantic question this layer cannot answer — which is why escalations go to a
human, not to an auto-approver.
"""

from __future__ import annotations

import re
import time
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Any, Deque, Dict, List, Optional, Tuple

import yaml


@dataclass
class Verdict:
    action: str            # "allow" | "deny" | "escalate"
    rule: str = ""         # which predicate fired
    detail: str = ""       # human-readable specifics

    @property
    def blocked(self) -> bool:
        return self.action in ("deny", "escalate")


ALLOW = Verdict("allow")


class PolicyError(Exception):
    """Raised when the policy file is missing or malformed (fail closed)."""


class PolicyEngine:
    def __init__(self, config: Dict[str, Any]):
        if not isinstance(config, dict):
            raise PolicyError("policy config must be a mapping")

        tools = config.get("tools") or {}
        allow = tools.get("allow")
        self.tool_allowlist: Optional[set] = set(allow) if allow is not None else None
        self.tool_denylist: set = set(tools.get("deny") or [])

        self.rate_limits: Dict[str, Tuple[int, float]] = {}
        for tool, rl in (tools.get("rate_limits") or {}).items():
            try:
                self.rate_limits[tool] = (int(rl["max_calls"]), float(rl["window_seconds"]))
            except (KeyError, TypeError, ValueError) as e:
                raise PolicyError(f"bad rate limit for tool {tool!r}: {e}") from e

        esc = config.get("escalation") or {}
        self.patterns: List[Tuple[re.Pattern, str]] = []
        for entry in esc.get("patterns") or []:
            try:
                self.patterns.append((re.compile(entry["pattern"]), str(entry.get("label", "unlabeled"))))
            except (re.error, KeyError, TypeError) as e:
                raise PolicyError(f"bad escalation pattern {entry!r}: {e}") from e

        session = config.get("session") or {}
        self.max_actions: Optional[int] = (
            int(session["max_actions"]) if session.get("max_actions") is not None else None
        )

        # runtime counters (in-memory; a production build would externalize these)
        self._tool_calls: Dict[Tuple[str, str], Deque[float]] = defaultdict(deque)
        self._session_actions: Dict[str, int] = defaultdict(int)

    # ------------------------------------------------------------------ load
    @classmethod
    def from_file(cls, path: str) -> "PolicyEngine":
        try:
            with open(path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
        except (OSError, yaml.YAMLError) as e:
            raise PolicyError(f"cannot load policy from {path}: {e}") from e
        return cls(config or {})

    # ------------------------------------------------------- session actions
    def register_action(self, session: str) -> Verdict:
        """Count one gated action against the session cap. Deny once exceeded."""
        if self.max_actions is not None and self._session_actions[session] >= self.max_actions:
            return Verdict(
                "deny",
                rule="session.max_actions",
                detail=f"session {session!r} exceeded max_actions={self.max_actions}",
            )
        self._session_actions[session] += 1
        return ALLOW

    # ------------------------------------------------------------ text scan
    def check_text(self, text: str) -> Verdict:
        """Dual-use escalation: regex/keyword match → block + flag for human review."""
        for pattern, label in self.patterns:
            m = pattern.search(text)
            if m:
                return Verdict(
                    "escalate",
                    rule=f"escalation.patterns[{label}]",
                    detail=f"matched {pattern.pattern!r} at offset {m.start()}",
                )
        return ALLOW

    # ------------------------------------------------------------ tool gates
    def check_tool_listed(self, tool: str) -> Verdict:
        """Allowlist/denylist check only (no rate-limit consumption).

        Used for tools *declared* in a request before any call happens.
        """
        if tool in self.tool_denylist:
            return Verdict("deny", rule="tools.deny", detail=f"tool {tool!r} is denylisted")
        if self.tool_allowlist is not None and tool not in self.tool_allowlist:
            return Verdict("deny", rule="tools.allow", detail=f"tool {tool!r} not in allowlist")
        return ALLOW

    def check_tool_call(self, session: str, tool: str) -> Verdict:
        """Full gate for an actual tool invocation: lists + per-tool rate limit."""
        listed = self.check_tool_listed(tool)
        if listed.blocked:
            return listed
        if tool in self.rate_limits:
            max_calls, window = self.rate_limits[tool]
            now = time.monotonic()
            calls = self._tool_calls[(session, tool)]
            while calls and now - calls[0] > window:
                calls.popleft()
            if len(calls) >= max_calls:
                return Verdict(
                    "deny",
                    rule="tools.rate_limits",
                    detail=f"tool {tool!r} exceeded {max_calls} calls / {window:g}s in session {session!r}",
                )
            calls.append(now)
        return ALLOW
