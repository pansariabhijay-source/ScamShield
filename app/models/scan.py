from __future__ import annotations

import uuid

from sqlalchemy import Enum, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDMixin
from app.db.types import GUID, JSONColumn
from app.models.enums import InputType, ScanStatus


class Scan(UUIDMixin, TimestampMixin, Base):
    """A single user-submitted artifact and its top-level verdict."""

    __tablename__ = "scans"

    user_id: Mapped[uuid.UUID] = mapped_column(
        GUID(), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    input_type: Mapped[InputType] = mapped_column(
        Enum(InputType, name="input_type"), nullable=False, index=True
    )
    status: Mapped[ScanStatus] = mapped_column(
        Enum(ScanStatus, name="scan_status"), default=ScanStatus.PENDING, nullable=False
    )

    # Raw input (text) and/or a reference to stored binary (object storage key).
    raw_content: Mapped[str | None] = mapped_column(Text, nullable=True)
    content_ref: Mapped[str | None] = mapped_column(String(512), nullable=True)
    extracted_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    meta: Mapped[dict] = mapped_column(JSONColumn(), default=dict)

    prediction: Mapped[Prediction | None] = relationship(  # noqa: F821
        back_populates="scan", uselist=False, cascade="all, delete-orphan"
    )
    user: Mapped[User] = relationship(back_populates="scans")  # noqa: F821

    __table_args__ = (
        Index("ix_scans_user_created", "user_id", "created_at"),
    )
