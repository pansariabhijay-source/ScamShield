"""Detector registry + ensemble factory.

Detectors are instantiated once (some hold loaded models) and cached. Adding a
new engine = append one line here. The ensemble is built from the registry so
the API/service layer never imports concrete detectors.
"""
from __future__ import annotations

from functools import lru_cache

from app.detectors.base import BaseDetector
from app.detectors.ensemble import EnsembleDetector
from app.detectors.impersonation_detector import ImpersonationDetector
from app.detectors.llm_detector import LLMDetector
from app.detectors.ocr_detector import OCRDetector
from app.detectors.text_detector import TextDetector
from app.detectors.upi_detector import UPIDetector
from app.detectors.url_detector import URLDetector


@lru_cache
def get_detectors() -> tuple[BaseDetector, ...]:
    return (
        TextDetector(),
        URLDetector(),
        OCRDetector(),
        UPIDetector(),
        ImpersonationDetector(),
        LLMDetector(),
    )


@lru_cache
def get_ensemble() -> EnsembleDetector:
    return EnsembleDetector(list(get_detectors()))
