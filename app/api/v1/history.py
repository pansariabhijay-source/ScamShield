from __future__ import annotations

import uuid

from fastapi import APIRouter, Query, status

from app.api.deps import CurrentUser, HistoryServiceDep
from app.schemas.common import Page
from app.schemas.detection import DetectionResult
from app.schemas.history import FeedbackRequest, ScanSummary

router = APIRouter(prefix="/history", tags=["history"])


@router.get("", response_model=Page[ScanSummary])
def list_history(
    user: CurrentUser,
    svc: HistoryServiceDep,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
) -> Page[ScanSummary]:
    items, total = svc.list_scans(user.id, page=page, size=size)
    return Page(items=items, total=total, page=page, size=size)


@router.get("/{scan_id}", response_model=DetectionResult)
def get_scan(
    scan_id: uuid.UUID, user: CurrentUser, svc: HistoryServiceDep
) -> DetectionResult:
    return svc.get_scan(user.id, scan_id)


@router.post("/{scan_id}/feedback", status_code=status.HTTP_201_CREATED)
def submit_feedback(
    scan_id: uuid.UUID,
    data: FeedbackRequest,
    user: CurrentUser,
    svc: HistoryServiceDep,
) -> dict:
    fb = svc.submit_feedback(user.id, scan_id, data)
    return {"id": str(fb.id), "status": "recorded"}
