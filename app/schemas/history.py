from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import InputType, RiskLevel, ScanStatus
from app.schemas.common import ORMModel


class ScanSummary(ORMModel):
    id: uuid.UUID
    input_type: InputType
    status: ScanStatus
    risk_level: RiskLevel | None = None
    scam_probability: int | None = None
    category: str | None = None
    created_at: datetime


class FeedbackRequest(BaseModel):
    label: str = Field(description="CORRECT | FALSE_POSITIVE | FALSE_NEGATIVE")
    comment: str | None = Field(default=None, max_length=2000)
