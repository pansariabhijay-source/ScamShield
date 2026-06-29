"""Ensemble risk engine.

Combines per-engine `DetectorResult`s into a single verdict using a
confidence-weighted, engine-weighted aggregation. Produces the final 0-100
probability, risk level, dominant category, deduplicated reasons, and a
recommendation. This is the only place fusion logic lives (single source of truth).
"""
from __future__ import annotations

from dataclasses import dataclass, field

from app.core.config import settings
from app.detectors.base import BaseDetector, DetectionContext, DetectorResult, Signal
from app.detectors.llm_detector import LLMDetector
from app.models.enums import RiskLevel

# Risk-level thresholds on the 0-100 scale.
_THRESHOLDS = [
    (85, RiskLevel.SCAM),
    (60, RiskLevel.HIGH_RISK),
    (30, RiskLevel.SUSPICIOUS),
    (0, RiskLevel.SAFE),
]


@dataclass
class EnsembleVerdict:
    scam_probability: int
    risk_level: RiskLevel
    confidence: float
    category: str | None
    reasons: list[str]
    recommendation: str
    risk_factors: list[Signal] = field(default_factory=list)
    engine_results: list[DetectorResult] = field(default_factory=list)
    model_version: str = "mvp-0.1.0"


class EnsembleDetector:
    """Not a BaseDetector — it *orchestrates* them (composition over inheritance)."""

    def __init__(self, detectors: list[BaseDetector]):
        self._detectors = detectors
        self._weights: dict[str, float] = settings.ENSEMBLE_WEIGHTS

    def run(self, ctx: DetectionContext) -> EnsembleVerdict:
        results: list[DetectorResult] = []
        # OCR first so downstream text engines see extracted text.
        ordered = sorted(self._detectors, key=lambda d: 0 if d.name == "ocr" else 1)
        for det in ordered:
            if det.applicable(ctx):
                results.append(det.analyze(ctx))

        # (a) Confidence-weighted, engine-weighted average — rewards agreement
        # across engines and respects per-engine trust (ENSEMBLE_WEIGHTS).
        # CRITICAL: only engines that actually fired a signal (score above a
        # small epsilon) participate. An engine returning score≈0 is *abstaining*
        # ("I found nothing"), which is NOT evidence of safety — averaging it in
        # would drag every verdict toward SAFE and destroy recall.
        contributing = [r for r in results if r.score > 0.02]
        weighted_sum = 0.0
        weight_total = 0.0
        for r in contributing:
            w = self._weights.get(r.detector, 0.1)
            effective = w * max(r.confidence, 0.05)
            weighted_sum += effective * r.score
            weight_total += effective
        weighted_avg = (weighted_sum / weight_total) if weight_total else 0.0

        # (b) Confidence-modulated noisy-OR — absence of a signal is NOT evidence
        # of safety, so silent engines (score≈0) leave the product unchanged and
        # a single strong engine still raises the aggregate risk.
        prod = 1.0
        for r in results:
            prod *= 1.0 - (r.score * max(r.confidence, 0.05))
        noisy_or = 1.0 - prod

        # Fuse: neither many-weak-signals (favours avg) nor one-strong-signal
        # (favours OR) should be lost.
        base = max(weighted_avg, noisy_or)

        # Escalation: a single very-high-confidence strong signal is decisive.
        strongest = max((r for r in results), key=lambda r: r.score * r.confidence, default=None)
        if strongest and strongest.score >= 0.8 and strongest.confidence >= 0.7:
            base = max(base, 0.85)

        # Uncorroborated-model guard: if the ONLY thing driving risk is the trained
        # text model (no concrete, explainable red flag from any engine — no scam
        # phrases, no bad URL, no impersonation, no UPI tell), treat it as soft
        # suspicion rather than a confident scam. The model alone is prone to
        # out-of-distribution false positives on legit transactional/delivery
        # messages, and a verdict we cannot *explain* should not read as decisive.
        concrete = [
            s for r in results for s in r.signals
            if s.weight > 0 and not s.code.startswith("text.ml")
        ]
        ml_only_suspicion = not concrete and base >= 0.45
        if ml_only_suspicion:
            base = min(base, 0.45)

        probability = int(round(min(1.0, base) * 100))
        risk_level = next(level for thr, level in _THRESHOLDS if probability >= thr)

        confidence = (
            sum(r.confidence for r in results) / len(results) if results else 0.0
        )
        if ml_only_suspicion:
            # We can't explain it — say so by reporting low confidence.
            confidence = min(confidence, 0.5)

        category = self._pick_category(results)
        reasons, factors = self._collect_reasons(results)
        recommendation = self._recommendation(results, risk_level, category)

        return EnsembleVerdict(
            scam_probability=probability,
            risk_level=risk_level,
            confidence=round(confidence, 3),
            category=category,
            reasons=reasons,
            recommendation=recommendation,
            risk_factors=factors,
            engine_results=results,
        )

    @staticmethod
    def _pick_category(results: list[DetectorResult]) -> str | None:
        # Prefer category from the highest-scoring engine that declared one.
        candidates = [
            (r.score * r.confidence, r.extra.get("category"))
            for r in results
            if r.extra.get("category")
        ]
        if not candidates:
            return None
        candidates.sort(reverse=True, key=lambda x: x[0])
        return candidates[0][1]

    @staticmethod
    def _collect_reasons(results: list[DetectorResult]):
        factors: list[Signal] = []
        for r in results:
            factors.extend(r.signals)
        # Highest-weight first, dedup descriptions.
        factors.sort(key=lambda s: s.weight, reverse=True)
        seen = set()
        reasons: list[str] = []
        for s in factors:
            if s.description not in seen:
                seen.add(s.description)
                reasons.append(s.description)
        return reasons[:8], factors

    @staticmethod
    def _recommendation(results, risk_level: RiskLevel, category: str | None) -> str:
        for r in results:
            if r.detector == "llm" and r.extra.get("recommendation"):
                return r.extra["recommendation"]
        return LLMDetector.render_recommendation(risk_level.value, category)
