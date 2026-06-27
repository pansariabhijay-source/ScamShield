from __future__ import annotations

from fastapi import APIRouter

from app.api.deps import StatsServiceDep
from app.schemas.stats import StatsOverview

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/overview", response_model=StatsOverview)
def stats_overview(svc: StatsServiceDep) -> StatsOverview:
    """Public aggregate metrics for the landing page (no authentication)."""
    return svc.overview()
