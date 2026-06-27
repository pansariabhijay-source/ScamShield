from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, PermissionError_
from app.models.enums import FeedbackLabel
from app.models.feedback import Feedback
from app.repositories.feedback_repo import FeedbackRepository
from app.repositories.scan_repo import ScanRepository
from app.schemas.detection import (
    DetectionResult,
    EngineScore,
    RiskFactorOut,
)
from app.schemas.history import FeedbackRequest, ScanSummary


class HistoryService:
    def __init__(self, db: Session):
        self.db = db
        self.scans = ScanRepository(db)
        self.feedback = FeedbackRepository(db)

    def list_scans(
        self, user_id: uuid.UUID, *, page: int, size: int
    ) -> tuple[list[ScanSummary], int]:
        rows, total = self.scans.list_for_user(
            user_id, limit=size, offset=(page - 1) * size
        )
        items = [
            ScanSummary(
                id=s.id,
                input_type=s.input_type,
                status=s.status,
                risk_level=s.prediction.risk_level if s.prediction else None,
                scam_probability=s.prediction.scam_probability if s.prediction else None,
                category=s.prediction.category_label if s.prediction else None,
                created_at=s.created_at,
            )
            for s in rows
        ]
        return items, total

    def get_scan(self, user_id: uuid.UUID, scan_id: uuid.UUID) -> DetectionResult:
        scan = self.scans.get_with_prediction(scan_id)
        if not scan:
            raise NotFoundError("Scan not found")
        if scan.user_id != user_id:
            raise PermissionError_("You do not have access to this scan")
        p = scan.prediction
        return DetectionResult(
            scan_id=scan.id,
            status=scan.status,
            input_type=scan.input_type,
            scam_probability=p.scam_probability if p else 0,
            risk_level=p.risk_level if p else "SAFE",
            confidence=p.confidence if p else 0.0,
            category=p.category_label if p else None,
            reasons=[rf.description for rf in (p.risk_factors if p else [])][:8],
            recommendation=p.recommendation if p else None,
            risk_factors=[
                RiskFactorOut(
                    detector=rf.detector, code=rf.code,
                    description=rf.description, weight=rf.weight,
                )
                for rf in (p.risk_factors if p else [])
            ],
            engine_scores=[
                EngineScore(detector=k, score=v.get("score", 0.0),
                            confidence=v.get("confidence", 0.0))
                for k, v in (p.engine_scores.items() if p and p.engine_scores else [])
            ],
            extracted_text=scan.extracted_text,
            model_version=p.model_version if p else "mvp-0.1.0",
            created_at=scan.created_at,
        )

    def submit_feedback(
        self, user_id: uuid.UUID, scan_id: uuid.UUID, data: FeedbackRequest
    ) -> Feedback:
        scan = self.scans.get(scan_id)
        if not scan or scan.user_id != user_id:
            raise NotFoundError("Scan not found")
        try:
            label = FeedbackLabel(data.label.upper())
        except ValueError as exc:
            raise NotFoundError(f"Invalid feedback label: {data.label}") from exc
        fb = Feedback(scan_id=scan_id, user_id=user_id, label=label, comment=data.comment)
        return self.feedback.add(fb)
