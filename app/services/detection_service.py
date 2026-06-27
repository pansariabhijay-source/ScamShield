"""Detection service — orchestrates engines, persists scan + prediction.

This is the application's transaction boundary for a detection: build context,
run the ensemble, materialize Scan/Prediction/RiskFactor rows, emit metrics,
and return a DTO. Routes stay thin; workers reuse the same method.
"""
from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.core.logging import get_logger
from app.core.observability import record_detection
from app.detectors.base import DetectionContext
from app.detectors.registry import get_ensemble
from app.models.enums import InputType, ScanStatus
from app.models.prediction import Prediction
from app.models.risk_factor import RiskFactor
from app.models.scan import Scan
from app.repositories.scan_repo import ScanRepository
from app.schemas.detection import DetectionResult, EngineScore, RiskFactorOut

logger = get_logger("scamshield.detection")


class DetectionService:
    def __init__(self, db: Session):
        self.db = db
        self.scans = ScanRepository(db)
        self.ensemble = get_ensemble()

    def detect(
        self,
        *,
        user_id: uuid.UUID,
        input_type: InputType,
        context: DetectionContext,
        raw_content: str | None = None,
        content_ref: str | None = None,
    ) -> DetectionResult:
        scan = Scan(
            user_id=user_id,
            input_type=input_type,
            status=ScanStatus.PROCESSING,
            raw_content=raw_content,
            content_ref=content_ref,
            meta=context.metadata or {},
        )
        self.scans.add(scan)

        verdict = self.ensemble.run(context)

        extracted = context.metadata.get("ocr_text")
        scan.extracted_text = extracted
        scan.status = ScanStatus.COMPLETED

        prediction = Prediction(
            scan_id=scan.id,
            scam_probability=verdict.scam_probability,
            confidence=verdict.confidence,
            risk_level=verdict.risk_level,
            category_label=verdict.category,
            recommendation=verdict.recommendation,
            engine_scores={
                r.detector: {"score": round(r.score, 4), "confidence": round(r.confidence, 4)}
                for r in verdict.engine_results
            },
            model_version=verdict.model_version,
        )
        self.db.add(prediction)
        self.db.flush()

        for s in verdict.risk_factors:
            detector = s.code.split(".", 1)[0]
            self.db.add(
                RiskFactor(
                    prediction_id=prediction.id,
                    detector=detector,
                    code=s.code,
                    description=s.description,
                    weight=s.weight,
                )
            )

        record_detection(input_type.value, verdict.risk_level.value)
        logger.info(
            "detection_completed",
            extra={
                "scan_id": str(scan.id),
                "input_type": input_type.value,
                "risk_level": verdict.risk_level.value,
                "probability": verdict.scam_probability,
            },
        )

        return DetectionResult(
            scan_id=scan.id,
            status=scan.status,
            input_type=input_type,
            scam_probability=verdict.scam_probability,
            risk_level=verdict.risk_level,
            confidence=verdict.confidence,
            category=verdict.category,
            reasons=verdict.reasons,
            recommendation=verdict.recommendation,
            risk_factors=[
                RiskFactorOut(
                    detector=s.code.split(".", 1)[0],
                    code=s.code,
                    description=s.description,
                    weight=s.weight,
                )
                for s in verdict.risk_factors
            ],
            engine_scores=[
                EngineScore(
                    detector=r.detector,
                    score=round(r.score, 4),
                    confidence=round(r.confidence, 4),
                    explanation=r.explanation,
                )
                for r in verdict.engine_results
            ],
            extracted_text=extracted,
            model_version=verdict.model_version,
            created_at=scan.created_at,
        )
