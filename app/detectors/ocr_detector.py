"""OCR engine.

Wraps EasyOCR/PaddleOCR behind a uniform interface. The detector's *job* is to
extract text and surface that text (plus low-level visual fraud hints). The
extracted text is then fed back through the text/UPI/impersonation engines by
the ensemble — OCR is a pre-processor that also contributes weak signals.
"""
from __future__ import annotations

from app.core.config import settings
from app.core.logging import get_logger
from app.detectors.base import BaseDetector, DetectionContext, DetectorResult, Signal

logger = get_logger("scamshield.ocr")


class OCREngine:
    """Lazy, swappable OCR backend."""

    _reader = None

    @classmethod
    def extract(cls, image_bytes: bytes) -> str:
        engine = settings.OCR_ENGINE
        if engine == "stub" or not settings.ENABLE_HEAVY_MODELS:
            return ""  # no OCR in lightweight mode; client may pass raw_text
        try:  # pragma: no cover - heavy path
            if engine == "easyocr":
                return cls._easyocr(image_bytes)
            if engine == "paddleocr":
                return cls._paddleocr(image_bytes)
        except Exception as exc:
            logger.warning("ocr_failed", extra={"engine": engine, "error": str(exc)})
        return ""

    @classmethod
    def _easyocr(cls, image_bytes: bytes) -> str:  # pragma: no cover
        import io

        import easyocr
        import numpy as np
        from PIL import Image

        if cls._reader is None:
            cls._reader = easyocr.Reader(["en"], gpu=False)
        img = np.array(Image.open(io.BytesIO(image_bytes)).convert("RGB"))
        return "\n".join(cls._reader.readtext(img, detail=0))

    @classmethod
    def _paddleocr(cls, image_bytes: bytes) -> str:  # pragma: no cover
        import io

        import numpy as np
        from paddleocr import PaddleOCR
        from PIL import Image

        if cls._reader is None:
            cls._reader = PaddleOCR(use_angle_cls=True, lang="en", show_log=False)
        img = np.array(Image.open(io.BytesIO(image_bytes)).convert("RGB"))
        result = cls._reader.ocr(img, cls=True)
        lines = [w[1][0] for block in (result or []) for w in block]
        return "\n".join(lines)


class OCRDetector(BaseDetector):
    name = "ocr"
    handles = ("image_bytes",)

    def _analyze(self, ctx: DetectionContext) -> DetectorResult:
        if not ctx.image_bytes:
            return DetectorResult(detector=self.name, score=0.0, confidence=0.0)

        text = OCREngine.extract(ctx.image_bytes)
        # Make extracted text available to the rest of the pipeline.
        if text:
            ctx.text = (ctx.text or "") + "\n" + text
            ctx.metadata["ocr_text"] = text

        signals: list[Signal] = []
        score = 0.0
        if not text:
            return DetectorResult(
                detector=self.name, score=0.0, confidence=0.2,
                explanation="No text extracted (OCR disabled or empty image).",
                extra={"extracted_text": ""},
            )

        # Weak visual-fraud heuristics on extracted text.
        lowered = text.lower()
        if "payment successful" in lowered or "transaction successful" in lowered:
            score += 0.10
            signals.append(Signal("ocr.payment_proof", "Image appears to be a payment-success screenshot", 0.10))

        return DetectorResult(
            detector=self.name,
            score=score,
            confidence=0.6,
            signals=signals,
            explanation=f"Extracted {len(text)} chars of text from image.",
            extra={"extracted_text": text},
        )
