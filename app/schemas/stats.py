from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class StatsTrendPoint(BaseModel):
    label: str  # weekday abbreviation, e.g. "Mon"
    count: int


class StatsCategory(BaseModel):
    category: str
    count: int


class StatsOverview(BaseModel):
    """Public, aggregate-only landing-page metrics. Contains no user content."""

    total_this_week: int = Field(ge=0)
    pct_change: int  # vs. the previous 7-day window (can be negative)
    trend: list[StatsTrendPoint]
    categories: list[StatsCategory]
    generated_at: datetime
