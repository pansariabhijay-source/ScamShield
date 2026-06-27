from __future__ import annotations

import uuid

from sqlalchemy import Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin
from app.db.types import GUID


class RiskFactor(UUIDMixin, TimestampMixin, Base):
    """A single explainability signal contributing to a prediction."""

    __tablename__ = "risk_factors"

    prediction_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("predictions.id", ondelete="CASCADE"),
        index=True,
    )
    detector: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    code: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    weight: Mapped[float] = mapped_column(Float, default=0.0)

    prediction: Mapped[Prediction] = relationship(  # noqa: F821
        back_populates="risk_factors"
    )
