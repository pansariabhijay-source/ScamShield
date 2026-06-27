"""FastAPI dependency-injection wiring.

Dependencies compose downward: DB session -> repositories/services, and the
auth chain (bearer token -> current user -> admin). Services are constructed
per-request with the request-scoped session — cheap and keeps them stateless.
"""
from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.exceptions import AuthError, PermissionError_
from app.core.logging import user_id_ctx
from app.core.security import ACCESS, decode_token
from app.db.session import get_db
from app.models.enums import UserRole
from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.services.admin_service import AdminService
from app.services.auth_service import AuthService
from app.services.detection_service import DetectionService
from app.services.history_service import HistoryService
from app.services.stats_service import StatsService

_bearer = HTTPBearer(auto_error=False)

DbDep = Annotated[Session, Depends(get_db)]


def get_current_user(
    db: DbDep,
    creds: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> User:
    if creds is None:
        raise AuthError("Missing authentication credentials")
    payload = decode_token(creds.credentials, expected_type=ACCESS)
    try:
        user_id = uuid.UUID(payload["sub"])
    except (KeyError, ValueError) as exc:
        raise AuthError("Malformed token subject") from exc

    user = UserRepository(db).get(user_id)
    if not user or not user.is_active:
        raise AuthError("User not found or inactive")
    user_id_ctx.set(str(user.id))  # log correlation
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_admin(user: CurrentUser) -> User:
    if user.role != UserRole.ADMIN:
        raise PermissionError_("Administrator privileges required")
    return user


AdminUser = Annotated[User, Depends(require_admin)]


# ---- Service providers ----
def get_auth_service(db: DbDep) -> AuthService:
    return AuthService(db)


def get_detection_service(db: DbDep) -> DetectionService:
    return DetectionService(db)


def get_history_service(db: DbDep) -> HistoryService:
    return HistoryService(db)


def get_admin_service(db: DbDep) -> AdminService:
    return AdminService(db)


def get_stats_service(db: DbDep) -> StatsService:
    return StatsService(db)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
DetectionServiceDep = Annotated[DetectionService, Depends(get_detection_service)]
HistoryServiceDep = Annotated[HistoryService, Depends(get_history_service)]
AdminServiceDep = Annotated[AdminService, Depends(get_admin_service)]
StatsServiceDep = Annotated[StatsService, Depends(get_stats_service)]
