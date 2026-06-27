from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.repositories.scan_repo import ScanRepository
from app.schemas.stats import StatsCategory, StatsOverview, StatsTrendPoint


class StatsService:
    """Aggregate, non-PII metrics for the public landing page.

    Reuses the same repository aggregations that power the admin analytics, but
    exposes only anonymous totals (counts by day and by scam category).
    """

    WINDOW_DAYS = 7

    def __init__(self, db: Session):
        self.db = db
        self.scans = ScanRepository(db)

    def overview(self) -> StatsOverview:
        now = datetime.now(UTC)
        this_week = self.scans.count_since(now - timedelta(days=self.WINDOW_DAYS))
        two_weeks = self.scans.count_since(now - timedelta(days=2 * self.WINDOW_DAYS))
        prev_week = max(two_weeks - this_week, 0)

        if prev_week:
            pct_change = round((this_week - prev_week) / prev_week * 100)
        else:
            pct_change = 100 if this_week else 0

        # 7-day scaffold so the chart is continuous even on quiet days.
        by_day = {row["day"]: row["total"] for row in self.scans.daily_timeseries(self.WINDOW_DAYS)}
        trend = [
            StatsTrendPoint(
                label=(d := (now - timedelta(days=i)).date()).strftime("%a"),
                count=by_day.get(d, 0),
            )
            for i in range(self.WINDOW_DAYS - 1, -1, -1)
        ]

        categories = [
            StatsCategory(category=row["category"], count=row["count"])
            for row in self.scans.top_categories(self.WINDOW_DAYS, limit=6)
        ]

        return StatsOverview(
            total_this_week=this_week,
            pct_change=pct_change,
            trend=trend,
            categories=categories,
            generated_at=now,
        )
