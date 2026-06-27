from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select
from sqlalchemy.orm import joinedload

from app.models.enums import RiskLevel
from app.models.prediction import Prediction
from app.models.scan import Scan
from app.repositories.base import BaseRepository


class ScanRepository(BaseRepository[Scan]):
    model = Scan

    def get_with_prediction(self, scan_id: uuid.UUID) -> Scan | None:
        stmt = (
            select(Scan)
            .options(joinedload(Scan.prediction).joinedload(Prediction.risk_factors))
            .where(Scan.id == scan_id)
        )
        return self.db.execute(stmt).unique().scalar_one_or_none()

    def list_for_user(
        self, user_id: uuid.UUID, *, limit: int, offset: int
    ) -> tuple[list[Scan], int]:
        base = select(Scan).where(Scan.user_id == user_id)
        total = self.db.execute(
            select(func.count()).select_from(base.subquery())
        ).scalar_one()
        rows = (
            self.db.execute(
                base.options(joinedload(Scan.prediction))
                .order_by(Scan.created_at.desc())
                .limit(limit)
                .offset(offset)
            )
            .unique()
            .scalars()
            .all()
        )
        return list(rows), total

    # ---- Admin analytics ----
    def count_all(self) -> int:
        return self.db.execute(select(func.count(Scan.id))).scalar_one()

    def count_since(self, since: datetime) -> int:
        return self.db.execute(
            select(func.count(Scan.id)).where(Scan.created_at >= since)
        ).scalar_one()

    def count_by_input_type(self) -> dict:
        rows = self.db.execute(
            select(Scan.input_type, func.count(Scan.id)).group_by(Scan.input_type)
        ).all()
        return {it.value: c for it, c in rows}

    def count_by_risk_level(self) -> dict:
        rows = self.db.execute(
            select(Prediction.risk_level, func.count(Prediction.id)).group_by(
                Prediction.risk_level
            )
        ).all()
        return {rl.value: c for rl, c in rows}

    def count_scams(self) -> int:
        return self.db.execute(
            select(func.count(Prediction.id)).where(
                Prediction.risk_level == RiskLevel.SCAM
            )
        ).scalar_one()

    def top_categories(self, window_days: int, limit: int = 10) -> list[dict]:
        since = datetime.now(UTC) - timedelta(days=window_days)
        rows = self.db.execute(
            select(Prediction.category_label, func.count(Prediction.id).label("c"))
            .where(Prediction.created_at >= since, Prediction.category_label.isnot(None))
            .group_by(Prediction.category_label)
            .order_by(func.count(Prediction.id).desc())
            .limit(limit)
        ).all()
        return [{"category": cat, "count": c} for cat, c in rows]

    def daily_timeseries(self, window_days: int) -> list[dict]:
        since = datetime.now(UTC) - timedelta(days=window_days)
        day = func.date_trunc("day", Scan.created_at).label("day")
        scams = func.count(Prediction.id).filter(
            Prediction.risk_level == RiskLevel.SCAM
        )
        rows = self.db.execute(
            select(day, func.count(Scan.id), scams)
            .select_from(Scan)
            .join(Prediction, Prediction.scan_id == Scan.id, isouter=True)
            .where(Scan.created_at >= since)
            .group_by(day)
            .order_by(day)
        ).all()
        return [
            {"day": d.date() if hasattr(d, "date") else d, "total": t, "scams": s or 0}
            for d, t, s in rows
        ]
