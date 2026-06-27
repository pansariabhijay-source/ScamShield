"""ScamShield AI — FastAPI application factory.

Wires logging, observability, exception handlers, CORS, routers and OpenAPI.
A factory (`create_app`) keeps the app testable and avoids import-time side
effects beyond logging configuration.
"""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.health import router as health_router
from app.api.router import api_router
from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging, get_logger
from app.core.observability import (
    RequestContextMiddleware,
    setup_sentry,
    setup_tracing,
)

configure_logging()
logger = get_logger("scamshield.app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("startup", extra={"environment": settings.ENVIRONMENT})
    # Warm detector singletons (loads any models once, not on first request).
    from app.detectors.registry import get_ensemble

    get_ensemble()
    yield
    logger.info("shutdown")


def create_app() -> FastAPI:
    setup_sentry()

    app = FastAPI(
        title=settings.APP_NAME,
        version="0.1.0",
        description=(
            "AI-powered scam detection platform. Submit text, URLs, emails, "
            "UPI payment details or screenshots and receive a calibrated scam "
            "risk verdict with explainable reasons and a recommended action."
        ),
        openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
        contact={"name": "ScamShield AI", "email": "security@scamshield.ai"},
        license_info={"name": "Proprietary"},
    )

    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(app)
    setup_tracing(app)

    app.include_router(health_router)
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    return app


app = create_app()
