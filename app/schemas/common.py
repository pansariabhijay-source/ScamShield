from __future__ import annotations

from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class Page(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int = Field(ge=1)
    size: int = Field(ge=1, le=200)

    @property
    def pages(self) -> int:
        return (self.total + self.size - 1) // self.size if self.size else 0


class HealthStatus(BaseModel):
    status: str
    service: str
    version: str
    timestamp: datetime
    checks: dict | None = None
