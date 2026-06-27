"""Enum definitions shared across models and schemas."""
from __future__ import annotations

import enum


class RiskLevel(str, enum.Enum):
    SAFE = "SAFE"
    SUSPICIOUS = "SUSPICIOUS"
    HIGH_RISK = "HIGH_RISK"
    SCAM = "SCAM"


class InputType(str, enum.Enum):
    TEXT = "TEXT"
    SMS = "SMS"
    EMAIL = "EMAIL"
    WHATSAPP = "WHATSAPP"
    URL = "URL"
    IMAGE = "IMAGE"
    UPI = "UPI"
    QR = "QR"


class ScanStatus(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class UserRole(str, enum.Enum):
    USER = "USER"
    ADMIN = "ADMIN"


class FeedbackLabel(str, enum.Enum):
    CORRECT = "CORRECT"
    FALSE_POSITIVE = "FALSE_POSITIVE"
    FALSE_NEGATIVE = "FALSE_NEGATIVE"
