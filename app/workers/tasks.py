from __future__ import annotations

import base64
import uuid

from app.core.logging import get_logger
from app.db.session import session_scope
from app.detectors.base import DetectionContext
from app.models.enums import InputType
from app.services.detection_service import DetectionService
from app.workers.celery_app import celery_app

logger = get_logger("scamshield.worker")


@celery_app.task(bind=True, max_retries=3, default_retry_delay=10)
def run_image_detection(self, user_id: str, image_b64: str, filename: str | None = None):
    """Async OCR + ensemble for screenshot/UPI/QR uploads."""
    try:
        image_bytes = base64.b64decode(image_b64)
        with session_scope() as db:
            svc = DetectionService(db)
            result = svc.detect(
                user_id=uuid.UUID(user_id),
                input_type=InputType.IMAGE,
                context=DetectionContext(
                    image_bytes=image_bytes, metadata={"filename": filename}
                ),
                content_ref=filename,
            )
            return result.model_dump(mode="json")
    except Exception as exc:  # pragma: no cover
        logger.exception("image_task_failed")
        raise self.retry(exc=exc) from exc


@celery_app.task
def rescore_batch(scan_ids: list[str]):
    """Re-run detection on a batch (e.g., after model upgrade)."""
    logger.info("rescore_batch_started", extra={"count": len(scan_ids)})
    # Implementation would load each scan's raw content and re-run the ensemble.
    return {"requested": len(scan_ids)}
