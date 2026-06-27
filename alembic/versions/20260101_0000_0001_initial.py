"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-01-01 00:00:00
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

UUID = postgresql.UUID(as_uuid=True)
JSONB = postgresql.JSONB


def _enum(name: str, *values: str) -> postgresql.ENUM:
    return postgresql.ENUM(*values, name=name, create_type=True)


def upgrade() -> None:
    user_role = _enum("user_role", "USER", "ADMIN")
    input_type = _enum("input_type", "TEXT", "SMS", "EMAIL", "WHATSAPP", "URL", "IMAGE", "UPI", "QR")
    scan_status = _enum("scan_status", "PENDING", "PROCESSING", "COMPLETED", "FAILED")
    risk_level = _enum("risk_level", "SAFE", "SUSPICIOUS", "HIGH_RISK", "SCAM")
    feedback_label = _enum("feedback_label", "CORRECT", "FALSE_POSITIVE", "FALSE_NEGATIVE")

    bind = op.get_bind()
    for e in (user_role, input_type, scan_status, risk_level, feedback_label):
        e.create(bind, checkfirst=True)

    op.create_table(
        "users",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("email", sa.String(320), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255)),
        sa.Column("role", user_role, nullable=False, server_default="USER"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()),
        sa.Column("is_verified", sa.Boolean, nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_created_at", "users", ["created_at"])

    op.create_table(
        "scam_categories",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("slug", sa.String(64), nullable=False),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("default_recommendation", sa.Text),
        sa.Column("is_active", sa.Boolean, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_scam_categories_slug", "scam_categories", ["slug"], unique=True)

    op.create_table(
        "scans",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("user_id", UUID, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("input_type", input_type, nullable=False),
        sa.Column("status", scan_status, nullable=False, server_default="PENDING"),
        sa.Column("raw_content", sa.Text),
        sa.Column("content_ref", sa.String(512)),
        sa.Column("extracted_text", sa.Text),
        sa.Column("meta", JSONB, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_scans_user_id", "scans", ["user_id"])
    op.create_index("ix_scans_input_type", "scans", ["input_type"])
    op.create_index("ix_scans_created_at", "scans", ["created_at"])
    op.create_index("ix_scans_user_created", "scans", ["user_id", "created_at"])

    op.create_table(
        "predictions",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("scan_id", UUID, sa.ForeignKey("scans.id", ondelete="CASCADE"), nullable=False),
        sa.Column("category_id", UUID, sa.ForeignKey("scam_categories.id", ondelete="SET NULL")),
        sa.Column("scam_probability", sa.Integer, nullable=False),
        sa.Column("confidence", sa.Float, nullable=False),
        sa.Column("risk_level", risk_level, nullable=False),
        sa.Column("category_label", sa.String(128)),
        sa.Column("recommendation", sa.Text),
        sa.Column("engine_scores", JSONB, server_default=sa.text("'{}'::jsonb")),
        sa.Column("model_version", sa.String(64), server_default="mvp-0.1.0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_predictions_scan_id", "predictions", ["scan_id"], unique=True)
    op.create_index("ix_predictions_category_id", "predictions", ["category_id"])
    op.create_index("ix_predictions_scam_probability", "predictions", ["scam_probability"])
    op.create_index("ix_predictions_risk_level", "predictions", ["risk_level"])
    op.create_index("ix_predictions_created_at", "predictions", ["created_at"])

    op.create_table(
        "risk_factors",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("prediction_id", UUID, sa.ForeignKey("predictions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("detector", sa.String(64), nullable=False),
        sa.Column("code", sa.String(64), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("weight", sa.Float, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_risk_factors_prediction_id", "risk_factors", ["prediction_id"])
    op.create_index("ix_risk_factors_detector", "risk_factors", ["detector"])

    op.create_table(
        "feedback",
        sa.Column("id", UUID, primary_key=True),
        sa.Column("scan_id", UUID, sa.ForeignKey("scans.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", UUID, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("label", feedback_label, nullable=False),
        sa.Column("comment", sa.Text),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_feedback_scan_id", "feedback", ["scan_id"])
    op.create_index("ix_feedback_user_id", "feedback", ["user_id"])


def downgrade() -> None:
    op.drop_table("feedback")
    op.drop_table("risk_factors")
    op.drop_table("predictions")
    op.drop_table("scans")
    op.drop_table("scam_categories")
    op.drop_table("users")
    for name in ("feedback_label", "risk_level", "scan_status", "input_type", "user_role"):
        op.execute(f"DROP TYPE IF EXISTS {name}")
