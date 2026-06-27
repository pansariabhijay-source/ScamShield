from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import AnyUrl, BaseModel, Field

from app.models.enums import InputType, RiskLevel, ScanStatus
from app.schemas.common import ORMModel


# ---------- Requests ----------
class TextDetectRequest(BaseModel):
    content: str = Field(min_length=1, max_length=20_000)
    input_type: InputType = InputType.TEXT
    metadata: dict = Field(default_factory=dict)


class URLDetectRequest(BaseModel):
    url: AnyUrl
    metadata: dict = Field(default_factory=dict)


class EmailDetectRequest(BaseModel):
    subject: str | None = Field(default=None, max_length=1000)
    sender: str | None = Field(default=None, max_length=320)
    body: str = Field(min_length=1, max_length=50_000)
    metadata: dict = Field(default_factory=dict)


class UPIDetectRequest(BaseModel):
    """Structured UPI request, or OCR'd text from a UPI screenshot."""

    payee_vpa: str | None = Field(default=None, max_length=255)
    payee_name: str | None = Field(default=None, max_length=255)
    amount: float | None = Field(default=None, ge=0)
    transaction_note: str | None = Field(default=None, max_length=1000)
    is_collect_request: bool = False
    raw_text: str | None = Field(default=None, max_length=10_000)
    metadata: dict = Field(default_factory=dict)


# ---------- Response components ----------
class RiskFactorOut(BaseModel):
    detector: str
    code: str
    description: str
    weight: float = 0.0


class EngineScore(BaseModel):
    detector: str
    score: float
    confidence: float
    explanation: str | None = None


class DetectionResult(ORMModel):
    scan_id: uuid.UUID
    status: ScanStatus
    input_type: InputType
    scam_probability: int = Field(ge=0, le=100)
    risk_level: RiskLevel
    confidence: float = Field(ge=0, le=1)
    category: str | None = None
    reasons: list[str] = Field(default_factory=list)
    recommendation: str | None = None
    risk_factors: list[RiskFactorOut] = Field(default_factory=list)
    engine_scores: list[EngineScore] = Field(default_factory=list)
    extracted_text: str | None = None
    model_version: str = "mvp-0.1.0"
    created_at: datetime


class AsyncJobAccepted(BaseModel):
    scan_id: uuid.UUID
    status: ScanStatus = ScanStatus.PROCESSING
    task_id: str
    poll_url: str
