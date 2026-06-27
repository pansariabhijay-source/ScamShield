from __future__ import annotations

import uuid

from sqlalchemy import Enum, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, TimestampMixin, UUIDMixin
from app.db.types import GUID
from app.models.enums import FeedbackLabel


class Feedback(UUIDMixin, TimestampMixin, Base):
    """User-reported correctness of a prediction. Fuels active-learning loop."""

    __tablename__ = "feedback"

    scan_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("scans.id", ondelete="CASCADE"), index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    label: Mapped[FeedbackLabel] = mapped_column(
        Enum(FeedbackLabel, name="feedback_label"), nullable=False
    )
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
