"""Portable column types.

Models target PostgreSQL in production but the unit-test suite runs against
SQLite. These helpers emit the native Postgres type (UUID/JSONB) on Postgres
and a portable fallback elsewhere, so one model definition serves both.
"""
from __future__ import annotations

from sqlalchemy import JSON, Uuid
from sqlalchemy.dialects.postgresql import JSONB


def GUID():
    # SQLAlchemy 2.0 Uuid -> native UUID on PG, CHAR(32) elsewhere.
    return Uuid(as_uuid=True)


def JSONColumn():
    return JSON().with_variant(JSONB(), "postgresql")
