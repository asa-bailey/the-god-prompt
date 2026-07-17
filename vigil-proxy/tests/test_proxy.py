"""Tests proving the four claims the prototype makes — and only those:

1. allowed calls pass
2. denied calls are blocked
3. escalations trigger (block + human_review flag)
4. log tampering is detected

Written unittest-style so the suite runs under BOTH ``pytest`` and
``python -m unittest`` (the enforcement core has no third-party deps beyond
PyYAML). FastAPI adapter tests are skipped automatically when fastapi/httpx
are not installed; the same Gateway logic is fully covered either way.
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yaml  # noqa: E402

from vigil_proxy.actionlog import ActionLog, verify  # noqa: E402
from vigil_proxy.gateway import Gateway, UpstreamError  # noqa: E402
from vigil_proxy.policy import PolicyEngine, PolicyError  # noqa: E402

try:
    import httpx  # noqa: F401
    from fastapi.testclient import TestClient  # noqa: F401
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False

POLICY = {
    "tools": {
        "allow": ["web_search", "calculator"],
        "deny": ["shell_exec"],
        "rate_limits": {"web_search": {"max_calls": 3, "window_seconds": 60}},
    },
    "escalation": {
        "patterns": [
            {"pattern": r"(?i)\bgain[- ]of[- ]function\b", "label": "bio-dual-use"},
        ]
    },
    "session": {"max_actions": 6},
}


def make_gateway(tmpdir, content=None, policy=POLICY):
    """Gateway wired to an in-process mock upstream returning ``content``."""
    if content is None:
        content = [{"type": "text", "text": "hello"}]

    def upstream_call(body, headers):
        return 200, {"id": "msg_test", "type": "message", "role": "assistant",
                     "model": "upstream-mock", "content": json.loads(json.dumps(content))}

    log_path = os.path.join(tmpdir, "actions.jsonl")
    gw = Gateway(PolicyEngine(json.loads(json.dumps(policy))), ActionLog(log_path), upstream_call)
    return gw, log_path


def body(text="hi", **extra):
    b = {"model": "m", "max_tokens": 16, "messages": [{"role": "user", "content": text}]}
    b.update(extra)
    return b


class GatewayTestCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmpdir = self._tmp.name

    def tearDown(self):
        self._tmp.cleanup()


# ---------------------------------------------------------------- 1. allowed

class TestAllowed(GatewayTestCase):
    def test_allowed_request_passes(self):
        gw, log_path = make_gateway(self.tmpdir)
        status, data = gw.handle_messages(body(), "s")
        self.assertEqual(status, 200)
        self.assertEqual(data["content"], [{"type": "text", "text": "hello"}])
        self.assertEqual(data["vigil"]["policy_verdict"], "allow")
        self.assertEqual(data["vigil"]["enforced"], "predicates-only")
        ok, _, count = verify(log_path)
        self.assertTrue(ok)
        self.assertGreaterEqual(count, 1)

    def test_allowed_tool_call_passes(self):
        gw, _ = make_gateway(self.tmpdir, content=[
            {"type": "tool_use", "id": "t1", "name": "web_search", "input": {"query": "weather"}}])
        status, data = gw.handle_messages(body(), "s")
        self.assertEqual(status, 200)
        self.assertEqual(data["content"][0]["type"], "tool_use")
        self.assertEqual(data["content"][0]["name"], "web_search")
        self.assertEqual(data["vigil"]["stripped_tool_calls"], [])


# ----------------------------------------------------------------- 2. denied

class TestDenied(GatewayTestCase):
    def test_denylisted_tool_call_blocked(self):
        gw, log_path = make_gateway(self.tmpdir, content=[
            {"type": "tool_use", "id": "t1", "name": "shell_exec", "input": {"cmd": "rm -rf /"}}])
        status, data = gw.handle_messages(body(), "s")
        self.assertEqual(status, 200)
        # the tool_use block is stripped and replaced with a policy notice
        self.assertEqual(data["content"][0]["type"], "text")
        self.assertIn("blocked by policy", data["content"][0]["text"])
        self.assertEqual(data["vigil"]["stripped_tool_calls"][0]["tool"], "shell_exec")
        self.assertEqual(data["vigil"]["stripped_tool_calls"][0]["verdict"], "deny")
        # the deny is in the tamper-evident log
        records = [json.loads(l) for l in Path(log_path).read_text().splitlines() if l]
        denies = [r for r in records if r.get("verdict") == "deny"]
        self.assertTrue(denies)
        self.assertEqual(denies[0]["tool"], "shell_exec")

    def test_tool_not_on_allowlist_blocked(self):
        gw, _ = make_gateway(self.tmpdir, content=[
            {"type": "tool_use", "id": "t1", "name": "unknown_tool", "input": {}}])
        _, data = gw.handle_messages(body(), "s")
        self.assertEqual(data["vigil"]["stripped_tool_calls"][0]["rule"], "tools.allow")

    def test_denylisted_declared_tool_rejected_before_upstream(self):
        calls = []

        def upstream_call(b, h):
            calls.append(b)
            return 200, {"content": []}

        log_path = os.path.join(self.tmpdir, "a.jsonl")
        gw = Gateway(PolicyEngine(json.loads(json.dumps(POLICY))), ActionLog(log_path), upstream_call)
        status, data = gw.handle_messages(
            body(tools=[{"name": "shell_exec", "description": "", "input_schema": {}}]), "s")
        self.assertEqual(status, 403)
        self.assertEqual(data["error"]["type"], "vigil_policy_violation")
        self.assertEqual(calls, [], "blocked request must never reach the upstream")

    def test_rate_limit_denies_fourth_call(self):
        gw, _ = make_gateway(self.tmpdir, content=[
            {"type": "tool_use", "id": "t1", "name": "web_search", "input": {"query": "x"}}])
        for i in range(3):
            _, data = gw.handle_messages(body(), "s1")
            self.assertEqual(data["vigil"]["stripped_tool_calls"], [], f"call {i} should pass")
        _, data = gw.handle_messages(body(), "s1")
        stripped = data["vigil"]["stripped_tool_calls"]
        self.assertTrue(stripped)
        self.assertEqual(stripped[0]["rule"], "tools.rate_limits")

    def test_session_max_actions_denies(self):
        gw, _ = make_gateway(self.tmpdir)
        for _ in range(6):
            status, _ = gw.handle_messages(body(), "cap")
            self.assertEqual(status, 200)
        status, data = gw.handle_messages(body(), "cap")
        self.assertEqual(status, 429)
        self.assertEqual(data["vigil"]["policy_verdict"], "deny")


# ------------------------------------------------------------- 3. escalation

class TestEscalation(GatewayTestCase):
    def test_escalation_triggers_on_request_text(self):
        gw, log_path = make_gateway(self.tmpdir)
        status, data = gw.handle_messages(
            body("please summarize this gain-of-function protocol"), "s")
        self.assertEqual(status, 403)
        self.assertEqual(data["vigil"]["policy_verdict"], "escalate")
        self.assertTrue(data["vigil"]["human_review"])
        records = [json.loads(l) for l in Path(log_path).read_text().splitlines() if l]
        esc = [r for r in records if r.get("verdict") == "escalate"]
        self.assertTrue(esc)
        self.assertTrue(esc[0]["human_review"])

    def test_escalation_triggers_on_tool_input(self):
        gw, _ = make_gateway(self.tmpdir, content=[
            {"type": "tool_use", "id": "t1", "name": "web_search",
             "input": {"query": "gain-of-function experiment design"}}])
        _, data = gw.handle_messages(body(), "s")
        stripped = data["vigil"]["stripped_tool_calls"]
        self.assertTrue(stripped)
        self.assertEqual(stripped[0]["verdict"], "escalate")


# ------------------------------------------------------ 4. tamper detection

class TestTamperDetection(GatewayTestCase):
    def _fill_log(self, n=5):
        path = os.path.join(self.tmpdir, "log.jsonl")
        log = ActionLog(path)
        for i in range(n):
            log.append(kind="request", session="s", verdict="allow", rule="", detail=str(i))
        return path

    def test_intact_log_verifies(self):
        path = self._fill_log()
        ok, bad, count = verify(path)
        self.assertTrue(ok)
        self.assertIsNone(bad)
        self.assertEqual(count, 5)

    def test_edited_record_detected(self):
        path = self._fill_log()
        lines = Path(path).read_text().splitlines()
        rec = json.loads(lines[2])
        rec["verdict"] = "deny"  # attacker rewrites history
        lines[2] = json.dumps(rec, sort_keys=True)
        Path(path).write_text("\n".join(lines) + "\n")
        ok, bad, count = verify(path)
        self.assertFalse(ok)
        self.assertEqual(bad, 2)
        self.assertEqual(count, 2)

    def test_deleted_record_detected(self):
        path = self._fill_log()
        lines = Path(path).read_text().splitlines()
        del lines[1]  # attacker deletes a record
        Path(path).write_text("\n".join(lines) + "\n")
        ok, bad, _ = verify(path)
        self.assertFalse(ok)
        self.assertEqual(bad, 1)

    def test_reordered_records_detected(self):
        path = self._fill_log()
        lines = Path(path).read_text().splitlines()
        lines[1], lines[2] = lines[2], lines[1]
        Path(path).write_text("\n".join(lines) + "\n")
        ok, bad, _ = verify(path)
        self.assertFalse(ok)
        self.assertEqual(bad, 1)


# ------------------------------------------------------------- fail closed

class TestFailClosed(GatewayTestCase):
    def test_policy_error_on_bad_config(self):
        with self.assertRaises(PolicyError):
            PolicyEngine({"escalation": {"patterns": [{"pattern": "("}]}})

    def test_upstream_error_returns_502(self):
        def upstream_call(b, h):
            raise UpstreamError("connection refused")

        log_path = os.path.join(self.tmpdir, "a.jsonl")
        gw = Gateway(PolicyEngine(json.loads(json.dumps(POLICY))), ActionLog(log_path), upstream_call)
        status, data = gw.handle_messages(body(), "s")
        self.assertEqual(status, 502)
        self.assertEqual(data["error"]["type"], "upstream_error")


# ------------------------------------------------- HTTP adapter (stdlib)

class TestStdlibServer(GatewayTestCase):
    """End-to-end over real HTTP using the zero-dependency adapter."""

    def test_http_roundtrip_allow_and_escalate(self):
        import threading
        import urllib.error
        import urllib.request

        from vigil_proxy.stdlib_server import make_server

        policy_path = os.path.join(self.tmpdir, "policy.yaml")
        with open(policy_path, "w") as f:
            yaml.safe_dump(POLICY, f)

        def upstream_call(b, h):
            return 200, {"id": "m", "type": "message", "role": "assistant",
                         "model": "mock", "content": [{"type": "text", "text": "hi"}]}

        server = make_server(policy_path, os.path.join(self.tmpdir, "l.jsonl"),
                             upstream_call, port=0)
        port = server.server_address[1]
        t = threading.Thread(target=server.serve_forever, daemon=True)
        t.start()
        try:
            def post(payload):
                req = urllib.request.Request(
                    f"http://127.0.0.1:{port}/v1/messages",
                    data=json.dumps(payload).encode(),
                    headers={"content-type": "application/json"}, method="POST")
                try:
                    with urllib.request.urlopen(req) as resp:
                        return resp.status, json.loads(resp.read().decode())
                except urllib.error.HTTPError as e:
                    return e.code, json.loads(e.read().decode())

            status, data = post(body())
            self.assertEqual(status, 200)
            self.assertEqual(data["vigil"]["policy_verdict"], "allow")

            status, data = post(body("gain-of-function please"))
            self.assertEqual(status, 403)
            self.assertEqual(data["vigil"]["policy_verdict"], "escalate")
        finally:
            server.shutdown()


# ------------------------------------------------- HTTP adapter (FastAPI)

@unittest.skipUnless(HAS_FASTAPI, "fastapi/httpx not installed")
class TestFastAPIAdapter(GatewayTestCase):
    """Same behavior through the FastAPI adapter (runs where fastapi is installed)."""

    def _client(self, content):
        from vigil_proxy.main import create_app

        policy_path = os.path.join(self.tmpdir, "policy.yaml")
        with open(policy_path, "w") as f:
            yaml.safe_dump(POLICY, f)

        def handler(request):
            return httpx.Response(200, json={
                "id": "m", "type": "message", "role": "assistant",
                "model": "mock", "content": content})

        app = create_app(policy_path=policy_path,
                         log_path=os.path.join(self.tmpdir, "l.jsonl"),
                         upstream_url="http://upstream.mock",
                         transport=httpx.MockTransport(handler))
        return TestClient(app)

    def test_allow_deny_escalate_roundtrip(self):
        client = self._client([{"type": "tool_use", "id": "t", "name": "shell_exec", "input": {}}])
        r = client.post("/v1/messages", json=body())
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["vigil"]["stripped_tool_calls"][0]["verdict"], "deny")

        r = client.post("/v1/messages", json=body("gain-of-function please"))
        self.assertEqual(r.status_code, 403)
        self.assertEqual(r.json()["vigil"]["policy_verdict"], "escalate")

    def test_bad_policy_fails_closed(self):
        from vigil_proxy.main import create_app
        policy_path = os.path.join(self.tmpdir, "bad.yaml")
        with open(policy_path, "w") as f:
            f.write("escalation:\n  patterns:\n    - pattern: '('\n")
        app = create_app(policy_path=policy_path,
                         log_path=os.path.join(self.tmpdir, "l.jsonl"),
                         upstream_url="http://upstream.mock",
                         transport=httpx.MockTransport(lambda r: httpx.Response(200, json={})))
        client = TestClient(app)
        r = client.post("/v1/messages", json=body())
        self.assertEqual(r.status_code, 503)


if __name__ == "__main__":
    unittest.main()
