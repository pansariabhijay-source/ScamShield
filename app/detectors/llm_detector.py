"""LLM reasoning engine.

Generates human-readable explanations and recommendations, and optionally a
second-opinion risk score. Provider-agnostic: defaults to Anthropic Claude
(claude-haiku-4-5 for low-latency/low-cost reasoning). Falls back to a fully
deterministic template generator so the platform never hard-depends on an
external API for a verdict.
"""
from __future__ import annotations

import json

from app.core.config import settings
from app.core.logging import get_logger
from app.detectors.base import BaseDetector, DetectionContext, DetectorResult, Signal

logger = get_logger("scamshield.llm")

_SYSTEM = (
    "You are a fraud-analysis assistant. Given a suspicious message, respond with "
    "a strict JSON object: {\"risk\": 0-1 float, \"category\": string, "
    "\"reasons\": [string], \"recommendation\": string}. Be concise and factual."
)


class LLMDetector(BaseDetector):
    name = "llm"
    handles = ("text",)

    def __init__(self) -> None:
        self._client = None
        if settings.LLM_PROVIDER == "anthropic" and settings.LLM_API_KEY:
            self._init_anthropic()

    def _init_anthropic(self) -> None:  # pragma: no cover - network path
        try:
            import anthropic

            self._client = anthropic.Anthropic(api_key=settings.LLM_API_KEY)
        except Exception as exc:
            logger.warning("anthropic_init_failed", extra={"error": str(exc)})
            self._client = None

    def _analyze(self, ctx: DetectionContext) -> DetectorResult:
        text = (ctx.text or "").strip()
        if not text:
            return DetectorResult(detector=self.name, score=0.0, confidence=0.0)

        if self._client is not None:  # pragma: no cover - network path
            try:
                return self._analyze_with_llm(text)
            except Exception as exc:
                logger.warning("llm_call_failed", extra={"error": str(exc)})

        return self._fallback(text)

    def _analyze_with_llm(self, text: str) -> DetectorResult:  # pragma: no cover
        msg = self._client.messages.create(
            model=settings.LLM_MODEL,
            max_tokens=512,
            system=_SYSTEM,
            messages=[{"role": "user", "content": text[:8000]}],
        )
        payload = json.loads(msg.content[0].text)
        reasons = payload.get("reasons", [])
        return DetectorResult(
            detector=self.name,
            score=float(payload.get("risk", 0.0)),
            confidence=0.7,
            signals=[Signal(f"llm.reason_{i}", r, 0.0) for i, r in enumerate(reasons)],
            explanation=payload.get("recommendation"),
            extra={"category": payload.get("category"),
                   "recommendation": payload.get("recommendation")},
        )

    def _fallback(self, text: str) -> DetectorResult:
        """Deterministic reasoning when no LLM is configured.

        Note: contributes 0 score weight (it only narrates) so it never inflates
        the ensemble; the ensemble passes the aggregate back for recommendation.
        """
        return DetectorResult(
            detector=self.name,
            score=0.0,
            confidence=0.0,
            signals=[],
            explanation=None,
            extra={"mode": "template"},
        )

    @staticmethod
    def render_recommendation(risk_level: str, category: str | None) -> str:
        base = {
            "SAFE": "No action needed. Stay alert to unsolicited requests.",
            "SUSPICIOUS": "Be cautious. Do not click links or share details until you verify the sender through official channels.",
            "HIGH_RISK": "Likely fraudulent. Do not respond, click links, scan QR codes or share OTP/PIN/personal data.",
            "SCAM": "Do not click links or share information. Block the sender and report to your bank / cybercrime portal (1930 in India).",
        }.get(risk_level, "Exercise caution.")
        if category:
            return f"{base} (Detected pattern: {category}.)"
        return base
