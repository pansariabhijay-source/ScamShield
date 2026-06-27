"""Password hashing + JWT issue/verify.

Access and refresh tokens are both JWTs distinguished by a `type` claim so a
refresh token can never be used as an access token and vice-versa.
"""
from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from passlib.context import CryptContext

from app.core.config import settings
from app.core.exceptions import AuthError

_pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

ACCESS = "access"
REFRESH = "refresh"


def hash_password(plain: str) -> str:
    return _pwd.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    return _pwd.verify(plain, hashed)


def _create_token(subject: str, token_type: str, expires_delta: timedelta,
                  extra: dict[str, Any] | None = None) -> str:
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": subject,
        "type": token_type,
        "iat": now,
        "exp": now + expires_delta,
        "jti": str(uuid.uuid4()),
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_access_token(subject: str, **extra: Any) -> str:
    return _create_token(
        subject, ACCESS,
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES), extra,
    )


def create_refresh_token(subject: str, **extra: Any) -> str:
    return _create_token(
        subject, REFRESH,
        timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS), extra,
    )


def decode_token(token: str, expected_type: str | None = None) -> dict[str, Any]:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
    except jwt.ExpiredSignatureError as exc:
        raise AuthError("Token has expired") from exc
    except jwt.PyJWTError as exc:
        raise AuthError("Invalid token") from exc

    if expected_type and payload.get("type") != expected_type:
        raise AuthError(f"Expected {expected_type} token")
    return payload
