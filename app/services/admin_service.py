from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.repositories.scan_repo import ScanRepository
from app.repositories.user_repo import UserRepository
from app.schemas.admin import PlatformStats, ScamTrends, TrendPoint


class AdminService:
    def __init__(self, db: Session):
        self.db = db
        self.scans = ScanRepository(db)
        self.users = UserRepository(db)

    def platform_stats(self) -> PlatformStats:
        since = datetime.now(UTC) - timedelta(hours=24)
        return PlatformStats(
            total_users=self.users.count(),
            total_scans=self.scans.count_all(),
            scans_last_24h=self.scans.count_since(since),
            scams_detected=self.scans.count_scams(),
            by_risk_level=self.scans.count_by_risk_level(),
            by_input_type=self.scans.count_by_input_type(),
        )

    def scam_trends(self, window_days: int = 30) -> ScamTrends:
        return ScamTrends(
            window_days=window_days,
            top_categories=self.scans.top_categories(window_days),
            timeseries=[
                TrendPoint(day=row["day"], total=row["total"], scams=row["scams"])
                for row in self.scans.daily_timeseries(window_days)
            ],
        )
