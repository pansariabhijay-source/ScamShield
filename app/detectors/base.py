"""Detector abstractions.

Every detection engine implements `BaseDetector.analyze` and returns a
normalized `DetectorResult`. This is the Liskov-substitutable contract that
lets the ensemble treat all engines uniformly and lets us hot-swap a heuristic
implementation for a real ML model with no downstream changes.
"""
from __future__ import annotations

import abc
import time
from dataclasses import dataclass, field
from typing import Any

from app.core.logging import get_logger
from app.core.observability import observe_detector

logger = get_logger("scamshield.detector")


@dataclass
class Signal:
    """An individual explainable risk signal."""

    code: str
    description: str
    weight: float = 0.0


@dataclass
class DetectorResult:
    """Normalized output of any detector.

    score:       0..1 likelihood that the input is a scam (per this engine).
    confidence:  0..1 how much this engine trusts its own score.
    signals:     human-readable contributing factors (explainability).
    """

    detector: str
    score: float = 0.0
    confidence: float = 0.0
    signals: list[Signal] = field(default_factory=list)
    explanation: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    def clamp(self) -> DetectorResult:
        self.score = max(0.0, min(1.0, self.score))
        self.confidence = max(0.0, min(1.0, self.confidence))
        return self


@dataclass
class DetectionContext:
    """Everything an engine might need. Engines pick what's relevant."""

    text: str | None = None
    url: str | None = None
    image_bytes: bytes | None = None
    email_subject: str | None = None
    email_sender: str | None = None
    upi: dict[str, Any] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class BaseDetector(abc.ABC):
    """Abstract base for all detection engines."""

    name: str = "base"
    #: input keys this detector can act on; used by the ensemble to skip N/A engines
    handles: tuple = ()

    @abc.abstractmethod
    def _analyze(self, ctx: DetectionContext) -> DetectorResult:
        """Engine-specific logic. Implementations must be pure + side-effect free."""

    def applicable(self, ctx: DetectionContext) -> bool:
        """Whether this engine has enough input to contribute."""
        if not self.handles:
            return True
        return any(getattr(ctx, h, None) for h in self.handles)

    def analyze(self, ctx: DetectionContext) -> DetectorResult:
        """Public entrypoint: times execution and guarantees a clamped result."""
        start = time.perf_counter()
        try:
            result = self._analyze(ctx)
        except Exception as exc:  # an engine failure must not crash the ensemble
            logger.warning(
                "detector_failed",
                extra={"detector": self.name, "error": str(exc)},
            )
            result = DetectorResult(detector=self.name, score=0.0, confidence=0.0)
        finally:
            observe_detector(self.name, time.perf_counter() - start)
        return result.clamp()
