"""Prometheus metrics, OpenTelemetry tracing, request-id middleware, Sentry hook.

All observability concerns are centralized so `main.py` wires them with a
single call. Everything degrades gracefully if optional deps are absent.
"""
from __future__ import annotations

import time
import uuid

from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings
from app.core.logging import get_logger, request_id_ctx

logger = get_logger("scamshield.http")

try:
    from prometheus_client import (
        CONTENT_TYPE_LATEST,
        Counter,
        Histogram,
        generate_latest,
    )

    REQUEST_COUNT = Counter(
        "scamshield_http_requests_total",
        "Total HTTP requests",
        ["method", "path", "status"],
    )
    REQUEST_LATENCY = Histogram(
        "scamshield_http_request_duration_seconds",
        "HTTP request latency",
        ["method", "path"],
    )
    DETECTION_COUNT = Counter(
        "scamshield_detections_total",
        "Total detections by risk level",
        ["input_type", "risk_level"],
    )
    DETECTOR_LATENCY = Histogram(
        "scamshield_detector_duration_seconds",
        "Per-detector latency",
        ["detector"],
    )
    _PROM = True
except Exception:  # pragma: no cover
    _PROM = False


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Assigns/propagates X-Request-ID, records latency + Prometheus counters."""

    async def dispatch(self, request: Request, call_next):
        rid = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        token = request_id_ctx.set(rid)
        start = time.perf_counter()
        # Route template (not raw path) keeps metric cardinality bounded.
        path_label = request.url.path
        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception:
            status_code = 500
            raise
        finally:
            elapsed = time.perf_counter() - start
            route = request.scope.get("route")
            if route is not None:
                path_label = getattr(route, "path", path_label)
            if _PROM and settings.METRICS_ENABLED:
                REQUEST_COUNT.labels(request.method, path_label, status_code).inc()
                REQUEST_LATENCY.labels(request.method, path_label).observe(elapsed)
            logger.info(
                "request_completed",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "status": status_code,
                    "duration_ms": round(elapsed * 1000, 2),
                },
            )
            request_id_ctx.reset(token)

        response.headers["X-Request-ID"] = rid
        return response


def record_detection(input_type: str, risk_level: str) -> None:
    if _PROM and settings.METRICS_ENABLED:
        DETECTION_COUNT.labels(input_type, risk_level).inc()


def observe_detector(detector: str, seconds: float) -> None:
    if _PROM and settings.METRICS_ENABLED:
        DETECTOR_LATENCY.labels(detector).observe(seconds)


def metrics_response():
    from fastapi import Response

    if not _PROM:
        return Response("prometheus_client not installed", media_type="text/plain")
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


def setup_tracing(app: FastAPI) -> None:
    if not settings.OTEL_ENABLED:
        return
    try:  # pragma: no cover - optional dependency
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
            OTLPSpanExporter,
        )
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        provider = TracerProvider(
            resource=Resource.create({"service.name": settings.APP_NAME})
        )
        provider.add_span_processor(
            BatchSpanProcessor(
                OTLPSpanExporter(endpoint=settings.OTEL_EXPORTER_OTLP_ENDPOINT)
            )
        )
        trace.set_tracer_provider(provider)
        FastAPIInstrumentor.instrument_app(app)
        logger.info("otel_tracing_enabled")
    except Exception as exc:
        logger.warning("otel_setup_failed", extra={"error": str(exc)})


def setup_sentry() -> None:
    if not settings.SENTRY_DSN:
        return
    try:  # pragma: no cover - optional dependency
        import sentry_sdk

        sentry_sdk.init(dsn=settings.SENTRY_DSN, environment=settings.ENVIRONMENT)
        logger.info("sentry_enabled")
    except Exception as exc:
        logger.warning("sentry_setup_failed", extra={"error": str(exc)})
