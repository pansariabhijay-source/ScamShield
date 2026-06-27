from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter
from sqlalchemy import text

from app.api.deps import DbDep
from app.core.config import settings
from app.core.observability import metrics_response
from app.schemas.common import HealthStatus

router = APIRouter(tags=["ops"])

_VERSION = "0.1.0"


@router.get("/health", response_model=HealthStatus)
def health() -> HealthStatus:
    """Liveness: process is up. Cheap, no dependencies."""
    return HealthStatus(
        status="ok",
        service=settings.APP_NAME,
        version=_VERSION,
        timestamp=datetime.now(UTC),
    )


@router.get("/ready", response_model=HealthStatus)
def ready(db: DbDep) -> HealthStatus:
    """Readiness: dependencies (DB, Redis) reachable."""
    checks: dict = {}
    try:
        db.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception as exc:
        checks["database"] = f"error: {exc}"

    try:
        import redis

        redis.Redis.from_url(settings.REDIS_URL).ping()
        checks["redis"] = "ok"
    except Exception as exc:
        checks["redis"] = f"error: {exc}"

    healthy = all(v == "ok" for v in checks.values())
    return HealthStatus(
        status="ready" if healthy else "degraded",
        service=settings.APP_NAME,
        version=_VERSION,
        timestamp=datetime.now(UTC),
        checks=checks,
    )


@router.get("/metrics")
def metrics():
    """Prometheus scrape endpoint."""
    return metrics_response()
