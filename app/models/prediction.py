from __future__ import annotations

import uuid

from sqlalchemy import Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin
from app.db.types import GUID, JSONColumn
from app.models.enums import RiskLevel


class Prediction(UUIDMixin, TimestampMixin, Base):
    """The ensemble verdict for a scan, plus per-engine raw scores."""

    __tablename__ = "predictions"

    scan_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("scans.id", ondelete="CASCADE"),
        unique=True,
        index=True,
    )
    category_id: Mapped[uuid.UUID | None] = mapped_column(
        GUID(),
        ForeignKey("scam_categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    scam_probability: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    risk_level: Mapped[RiskLevel] = mapped_column(
        Enum(RiskLevel, name="risk_level"), nullable=False, index=True
    )
    category_label: Mapped[str | None] = mapped_column(String(128), nullable=True)
    recommendation: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Per-engine score breakdown for auditability / model debugging.
    engine_scores: Mapped[dict] = mapped_column(JSONColumn(), default=dict)
    model_version: Mapped[str] = mapped_column(String(64), default="mvp-0.1.0")

    scan: Mapped[Scan] = relationship(back_populates="prediction")  # noqa: F821
    category: Mapped[ScamCategory | None] = relationship()  # noqa: F821
    risk_factors: Mapped[list[RiskFactor]] = relationship(  # noqa: F821
        back_populates="prediction", cascade="all, delete-orphan"
    )
