from __future__ import annotations

from fastapi import APIRouter, Query

from app.api.deps import AdminServiceDep, AdminUser
from app.schemas.admin import PlatformStats, ScamTrends

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stats", response_model=PlatformStats)
def platform_stats(_: AdminUser, svc: AdminServiceDep) -> PlatformStats:
    return svc.platform_stats()


@router.get("/scam-trends", response_model=ScamTrends)
def scam_trends(
    _: AdminUser,
    svc: AdminServiceDep,
    window_days: int = Query(30, ge=1, le=365),
) -> ScamTrends:
    return svc.scam_trends(window_days)
