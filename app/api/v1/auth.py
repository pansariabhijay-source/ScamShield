from __future__ import annotations

from fastapi import APIRouter, status

from app.api.deps import AuthServiceDep, CurrentUser
from app.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenPair,
    UserPublic,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def register(data: RegisterRequest, svc: AuthServiceDep) -> UserPublic:
    user = svc.register(data)
    return UserPublic.model_validate(user)


@router.post("/login", response_model=TokenPair)
def login(data: LoginRequest, svc: AuthServiceDep) -> TokenPair:
    user = svc.authenticate(data.email, data.password)
    return svc.issue_tokens(user)


@router.post("/refresh", response_model=TokenPair)
def refresh(data: RefreshRequest, svc: AuthServiceDep) -> TokenPair:
    return svc.refresh(data.refresh_token)


@router.get("/me", response_model=UserPublic)
def me(user: CurrentUser) -> UserPublic:
    return UserPublic.model_validate(user)
