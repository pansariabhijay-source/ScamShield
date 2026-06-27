from __future__ import annotations

from datetime import date

from pydantic import BaseModel


class PlatformStats(BaseModel):
    total_users: int
    total_scans: int
    scans_last_24h: int
    scams_detected: int
    by_risk_level: dict[str, int]
    by_input_type: dict[str, int]


class TrendPoint(BaseModel):
    day: date
    total: int
    scams: int


class ScamTrends(BaseModel):
    window_days: int
    top_categories: list[dict[str, object]]
    timeseries: list[TrendPoint]
