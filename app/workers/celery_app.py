"""Celery application.

Heavy/slow detection (OCR on large images, LLM second-opinion, batch
re-scoring) runs here so the API stays low-latency. The same DetectionService
is reused inside tasks via `session_scope`.
"""
from __future__ import annotations

from celery import Celery

from app.core.config import settings
from app.core.logging import configure_logging

configure_logging()

celery_app = Celery(
    "scamshield",
    broker=settings.celery_broker,
    backend=settings.celery_backend,
    include=["app.workers.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_acks_late=True,
    worker_prefetch_multiplier=1,  # fair dispatch for heavy ML tasks
    task_track_started=True,
    result_expires=3600,
    task_default_queue="default",
    task_routes={
        "app.workers.tasks.run_image_detection": {"queue": "ml"},
        "app.workers.tasks.run_llm_reasoning": {"queue": "ml"},
    },
    task_time_limit=120,
    task_soft_time_limit=100,
)
