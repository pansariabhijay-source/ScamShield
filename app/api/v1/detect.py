from __future__ import annotations

from fastapi import APIRouter, File, Form, UploadFile, status

from app.api.deps import CurrentUser, DetectionServiceDep
from app.detectors.base import DetectionContext
from app.models.enums import InputType
from app.schemas.detection import (
    DetectionResult,
    EmailDetectRequest,
    TextDetectRequest,
    UPIDetectRequest,
    URLDetectRequest,
)

router = APIRouter(prefix="/detect", tags=["detection"])

_MAX_IMAGE_BYTES = 10 * 1024 * 1024  # 10 MB


@router.post("/text", response_model=DetectionResult)
def detect_text(
    data: TextDetectRequest, user: CurrentUser, svc: DetectionServiceDep
) -> DetectionResult:
    ctx = DetectionContext(text=data.content, metadata=dict(data.metadata))
    return svc.detect(
        user_id=user.id,
        input_type=data.input_type,
        context=ctx,
        raw_content=data.content,
    )


@router.post("/url", response_model=DetectionResult)
def detect_url(
    data: URLDetectRequest, user: CurrentUser, svc: DetectionServiceDep
) -> DetectionResult:
    url = str(data.url)
    ctx = DetectionContext(url=url, text=url, metadata=dict(data.metadata))
    return svc.detect(
        user_id=user.id, input_type=InputType.URL, context=ctx, raw_content=url
    )


@router.post("/email", response_model=DetectionResult)
def detect_email(
    data: EmailDetectRequest, user: CurrentUser, svc: DetectionServiceDep
) -> DetectionResult:
    blob = "\n".join(filter(None, [data.subject, data.body]))
    ctx = DetectionContext(
        text=blob,
        email_subject=data.subject,
        email_sender=data.sender,
        metadata=dict(data.metadata),
    )
    return svc.detect(
        user_id=user.id, input_type=InputType.EMAIL, context=ctx, raw_content=blob
    )


@router.post("/upi", response_model=DetectionResult)
def detect_upi(
    data: UPIDetectRequest, user: CurrentUser, svc: DetectionServiceDep
) -> DetectionResult:
    ctx = DetectionContext(
        text=data.raw_text or data.transaction_note,
        upi=data.model_dump(),
        metadata=dict(data.metadata),
    )
    return svc.detect(
        user_id=user.id, input_type=InputType.UPI, context=ctx,
        raw_content=data.raw_text,
    )


@router.post("/image", response_model=DetectionResult, status_code=status.HTTP_200_OK)
async def detect_image(
    user: CurrentUser,
    svc: DetectionServiceDep,
    file: UploadFile = File(...),
    input_type: str = Form(default=InputType.IMAGE.value),
) -> DetectionResult:
    from app.core.exceptions import AppError

    content = await file.read()
    if len(content) > _MAX_IMAGE_BYTES:
        raise AppError("Image exceeds 10MB limit")
    try:
        itype = InputType(input_type)
    except ValueError:
        itype = InputType.IMAGE
    ctx = DetectionContext(image_bytes=content, metadata={"filename": file.filename})
    return svc.detect(
        user_id=user.id,
        input_type=itype,
        context=ctx,
        content_ref=file.filename,
    )
