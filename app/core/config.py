"""Application configuration via Pydantic Settings.

All runtime configuration is sourced from environment variables (12-factor).
A single cached `Settings` instance is exposed through `get_settings()` so the
object is constructed once per process and shared everywhere via DI.
"""
from __future__ import annotations

from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ----- App -----
    APP_NAME: str = "ScamShield AI"
    ENVIRONMENT: str = Field(default="development")  # development | staging | production
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"
    LOG_LEVEL: str = "INFO"
    LOG_JSON: bool = True

    # ----- Security / JWT -----
    SECRET_KEY: str = Field(default="change-me-in-production")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 14
    PASSWORD_BCRYPT_ROUNDS: int = 12

    # ----- Database -----
    POSTGRES_USER: str = "scamshield"
    POSTGRES_PASSWORD: str = "scamshield"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "scamshield"
    DATABASE_URL: str | None = None
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DB_ECHO: bool = False

    # ----- Redis / Celery -----
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str | None = None
    CELERY_RESULT_BACKEND: str | None = None

    # ----- CORS -----
    BACKEND_CORS_ORIGINS: list[str] = ["*"]

    # ----- ML / Detectors -----
    NLP_MODEL_NAME: str = "distilbert-base-uncased"
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    OCR_ENGINE: str = "easyocr"  # easyocr | paddleocr | stub
    ENABLE_HEAVY_MODELS: bool = False  # when False, detectors use heuristic fallbacks
    LLM_PROVIDER: str = "anthropic"  # anthropic | openai | stub
    LLM_MODEL: str = "claude-haiku-4-5-20251001"
    LLM_API_KEY: str | None = None

    # Ensemble weights (per engine). Tuned offline; overridable via env.
    ENSEMBLE_WEIGHTS: dict = {
        "text": 0.30,
        "url": 0.20,
        "impersonation": 0.20,
        "upi": 0.15,
        "ocr": 0.05,
        "llm": 0.10,
    }

    # ----- Observability -----
    OTEL_ENABLED: bool = False
    OTEL_EXPORTER_OTLP_ENDPOINT: str | None = None
    SENTRY_DSN: str | None = None
    METRICS_ENABLED: bool = True

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def _split_cors(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [o.strip() for o in v.split(",") if o.strip()]
        return v

    @property
    def sqlalchemy_database_uri(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return (
            f"postgresql+psycopg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def celery_broker(self) -> str:
        return self.CELERY_BROKER_URL or self.REDIS_URL

    @property
    def celery_backend(self) -> str:
        return self.CELERY_RESULT_BACKEND or self.REDIS_URL

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
