from __future__ import annotations

import uuid
from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.base import Base

M = TypeVar("M", bound=Base)


class BaseRepository(Generic[M]):
    """Thin generic repository isolating SQLAlchemy from the service layer."""

    model: type[M]

    def __init__(self, db: Session):
        self.db = db

    def get(self, id_: uuid.UUID) -> M | None:
        return self.db.get(self.model, id_)

    def add(self, obj: M) -> M:
        self.db.add(obj)
        self.db.flush()  # populate PK without committing (commit owned by UoW)
        return obj

    def delete(self, obj: M) -> None:
        self.db.delete(obj)

    def list(self, *, limit: int = 50, offset: int = 0):
        stmt = select(self.model).limit(limit).offset(offset)
        return list(self.db.execute(stmt).scalars())
