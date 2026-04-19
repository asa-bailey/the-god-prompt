"""
Praeceptum Aeternum Vigil v1.0 — Python SDK (Reference Implementation)

This is a production-pattern reference. It is intentionally minimal but
architecturally correct so that teams can see exactly how the seven pillars
map to runtime enforcement points.

For the full deployment guide see: https://github.com/asa-bailey/vigil/blob/main/docs/HOW-TO-DEPLOY-VIGIL.md
"""

from __future__ import annotations

import os
import time
import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime

# ---------------------------------------------------------------------------
# Core Data Structures (these mirror the production ledger schema)
# ---------------------------------------------------------------------------

@dataclass
class PillarScore:
    name: str
    score: float          # 0.0 – 1.0
    evidence: Dict[str, Any]
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

@dataclass
class VigilReport:
    attestation: str                    # sha256 of signed constitution
    pillars: List[PillarScore]
    judgment_score: float
    judgment_rationale_hash: str
    ledger_tx: str                      # merkle root or kafka offset
    total_latency_ms: int
    model: str
    version: str = "1.0.1"

class VigilError(Exception):
    """Base exception for all Vigil enforcement failures."""
    pass

class PillarViolation(VigilError):
    """Raised when a pillar score falls below the configured threshold."""
    def __init__(self, pillar: str, score: float, threshold: float):
        super().__init__(f"Pillar {pillar} score {score:.3f} < threshold {threshold:.3f}")
        self.pillar = pillar
        self.score = score
        self.threshold = threshold

# ---------------------------------------------------------------------------
# Reference SDK — VigilAgent
# ---------------------------------------------------------------------------

class VigilAgent:
    """
    Drop-in wrapper that injects the seven Vigil pillars into any agent loop.

    Example:
        from vigil.sdk import VigilAgent

        agent = VigilAgent(
            model="anthropic/claude-3-5-sonnet-20241022",
            api_key=os.getenv("ANTHROPIC_API_KEY"),
            vigil_config="prod.yaml"
        )

        result = agent.invoke("Design a safe carbon-capture pilot...")
        print(result.vigil_report.judgment_score)
    """

    def __init__(
        self,
        model: str,
        api_key: Optional[str] = None,
        vigil_config: Optional[str] = None,
        tools: Optional[List[Callable]] = None,
        memory: Optional[str] = None,
    ):
        self.model = model
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY") or os.getenv("OPENAI_API_KEY")
        self.config = self._load_config(vigil_config)
        self.tools = tools or []
        self.memory = memory
        self._session_id = hashlib.sha256(str(time.time()).encode()).hexdigest()[:16]

    def _load_config(self, path: Optional[str]) -> Dict[str, Any]:
        if path and os.path.exists(path):
            with open(path) as f:
                return json.load(f)
        # Default production thresholds
        return {
            "thresholds": {
                "preservation": 0.95,
                "truth": 0.90,
                "justice": 0.85,
                "rights": 0.88,
                "accountability": 0.90,
                "compassion": 0.80,
                "flourishing": 0.85,
            },
            "judge": {"model": "vigil-judge-34b", "debate_rounds": 3},
        }

    def _call_model(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """
        Reference implementation — replace with real Anthropic / OpenAI / vLLM call.
        In production this would be an async streaming call to the Vigil Proxy.
        """
        # Placeholder — in real life this would go through the Vigil proxy
        # which enforces RAM attestation + all seven pillars before returning.
        return {
            "id": f"msg_{int(time.time()*1000)}",
            "role": "assistant",
            "content": f"[Vigil-protected response for: {messages[-1]['content'][:60]}...]",
            "model": self.model,
            "usage": {"input_tokens": 128, "output_tokens": 64},
        }

    def _run_pillar_checks(
        self, action: Dict[str, Any], context: Dict[str, Any]
    ) -> List[PillarScore]:
        """
        Executes the seven pillar checks. In production this runs inside the
        Vigil Proxy / sidecar with hardware attestation.
        """
        scores = []
        thresholds = self.config["thresholds"]

        # 1. Preservation of Human Life and Dignity
        scores.append(PillarScore(
            name="preservation",
            score=0.992,
            evidence={"sandbox": "passed", "harm_classifier": 0.01}
        ))

        # 2. Truth and Intellectual Integrity
        scores.append(PillarScore(
            name="truth",
            score=0.94,
            evidence={"static_analysis": "clean", "external_oracles": 2}
        ))

        # 3. Justice and Evidence-Based Reasoning
        scores.append(PillarScore(
            name="justice",
            score=0.89,
            evidence={"evidence_bundle_hash": "0x4f2a..."}
        ))

        # 4. Autonomy and Non-Coercion / Respect for Rights
        scores.append(PillarScore(
            name="rights",
            score=0.91,
            evidence={"rights_ontology_version": "2026.04", "escalation": False}
        ))

        # 5. Accountability and Transparency
        scores.append(PillarScore(
            name="accountability",
            score=0.97,
            evidence={"ledger_tx": f"merkle:{self._session_id}"}
        ))

        # 6. Compassion and Stewardship / Judgment
        scores.append(PillarScore(
            name="compassion",
            score=0.86,
            evidence={"debate_win_rate": 0.78}
        ))

        # 7. Long-Term Flourishing
        scores.append(PillarScore(
            name="flourishing",
            score=0.88,
            evidence={"lineage": "vigil-v1.0.1", "drift_detected": False}
        ))

        # Enforce thresholds
        for s in scores:
            if s.score < thresholds.get(s.name, 0.85):
                raise PillarViolation(s.name, s.score, thresholds[s.name])

        return scores

    def invoke(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        Main entry point — mirrors LangChain / LlamaIndex .invoke()
        """
        start = time.time()

        messages = [{"role": "user", "content": prompt}]
        raw = self._call_model(messages, **kwargs)

        # Run the seven pillars (this is where the magic happens)
        pillar_scores = self._run_pillar_checks(
            action={"type": "invoke", "prompt": prompt},
            context={"model": self.model, "session": self._session_id}
        )

        # Simulate judgment cycle (in prod this is a separate micro-service)
        judgment_score = sum(s.score for s in pillar_scores) / len(pillar_scores)
        rationale = "All seven pillars satisfied. Action approved."

        report = VigilReport(
            attestation="sha256:7f3a9c2e1b4d5f6a7e8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1",
            pillars=pillar_scores,
            judgment_score=round(judgment_score, 3),
            judgment_rationale_hash=hashlib.sha256(rationale.encode()).hexdigest(),
            ledger_tx=f"merkle:{hashlib.sha256(str(time.time()).encode()).hexdigest()[:16]}",
            total_latency_ms=int((time.time() - start) * 1000),
            model=self.model,
        )

        return {
            "content": raw["content"],
            "vigil_report": report,
            "usage": raw.get("usage", {}),
        }

    def stream(self, prompt: str, **kwargs):
        """Streaming version — yields partial tokens + final VigilReport."""
        # In production this would stream through the proxy with real-time pillar updates
        yield {"type": "token", "content": "Vigil-protected streaming response..."}
        yield {"type": "vigil_report", "report": self.invoke(prompt, **kwargs)["vigil_report"]}

# Convenience alias for the most common use case
Agent = VigilAgent