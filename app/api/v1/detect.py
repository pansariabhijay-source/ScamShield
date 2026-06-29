from __future__ import annotations

import re
import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, File, Form, UploadFile, status

from app.api.deps import CurrentUser, DetectionServiceDep
from app.detectors.base import DetectionContext
from app.detectors.registry import get_ensemble
from app.models.enums import InputType, ScanStatus
from app.schemas.detection import (
    DetectionResult,
    EmailDetectRequest,
    EngineScore,
    RiskFactorOut,
    TextDetectRequest,
    UPIDetectRequest,
    URLDetectRequest,
)

router = APIRouter(prefix="/detect", tags=["detection"])

_MAX_IMAGE_BYTES = 10 * 1024 * 1024  # 10 MB

# Pull the first real URL out of a message so the URL engine contributes even
# when the user pastes free text containing a link. The final label must be an
# alphabetic TLD (>=2 letters) so amounts/version numbers like "Rs 239.88" or
# "v1.2" are NOT mistaken for domains.
_URL_IN_TEXT = re.compile(
    r"((?:https?://)?(?:www\.)?(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z]{2,}(?:/[^\s]*)?)",
    re.IGNORECASE,
)


def _verdict_to_result(
    verdict, input_type: InputType, extracted: str | None = None
) -> DetectionResult:
    """Map an EnsembleVerdict to the public DetectionResult DTO (no persistence)."""
    category = verdict.category
    if not category and verdict.scam_probability >= 30:
        # Surface a useful label even when no engine declared a named category.
        if any(r.detector == "url" and r.score > 0.25 for r in verdict.engine_results):
            category = "Phishing / Suspicious Link"
        else:
            category = "Suspicious Message"
    return DetectionResult(
        scan_id=uuid.uuid4(),
        status=ScanStatus.COMPLETED,
        input_type=input_type,
        scam_probability=verdict.scam_probability,
        risk_level=verdict.risk_level,
        confidence=verdict.confidence,
        category=category,
        reasons=verdict.reasons,
        recommendation=verdict.recommendation,
        risk_factors=[
            RiskFactorOut(detector=s.code.split(".", 1)[0], code=s.code,
                          description=s.description, weight=s.weight)
            for s in verdict.risk_factors
        ],
        engine_scores=[
            EngineScore(detector=r.detector, score=round(r.score, 4),
                        confidence=round(r.confidence, 4), explanation=r.explanation)
            for r in verdict.engine_results
        ],
        extracted_text=extracted,
        model_version=verdict.model_version,
        created_at=datetime.now(UTC),
    )


@router.post("/public/text", response_model=DetectionResult)
def detect_text_public(data: TextDetectRequest) -> DetectionResult:
    """Unauthenticated, non-persisting detection for the public demo.

    Runs the same trained ensemble as the authenticated endpoint, but stores
    nothing and requires no login ("No sign-up to try"). It also extracts an
    embedded URL so link-bearing messages get full URL-engine analysis.
    """
    ctx = DetectionContext(text=data.content, metadata=dict(data.metadata))
    if data.input_type == InputType.URL:
        ctx.url = data.content
    elif data.input_type == InputType.UPI:
        ctx.upi = {"raw_text": data.content}
    else:
        m = _URL_IN_TEXT.search(data.content)
        if m:
            ctx.url = m.group(1)
    verdict = get_ensemble().run(ctx)
    return _verdict_to_result(verdict, data.input_type)


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
