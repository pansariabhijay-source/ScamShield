from __future__ import annotations

import os

os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("SECRET_KEY", "test-secret")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# In-memory SQLite for fast, isolated unit tests. JSONB/UUID degrade gracefully
# via SQLAlchemy's generic types for the columns we exercise here.
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import create_app

TEST_DB_URL = "sqlite+pysqlite:///:memory:"


@pytest.fixture()
def engine():
    eng = create_engine(
        TEST_DB_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    # SQLite shim for postgres-only types used in models.

    Base.metadata.create_all(eng)
    yield eng
    Base.metadata.drop_all(eng)


@pytest.fixture()
def db_session(engine):
    TestingSession = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db_session):
    app = create_app()

    def _override_get_db():
        try:
            yield db_session
            db_session.commit()
        except Exception:
            db_session.rollback()
            raise

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def auth_headers(client):
    client.post(
        "/api/v1/auth/register",
        json={"email": "user@test.com", "password": "supersecret1", "full_name": "Test"},
    )
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": "user@test.com", "password": "supersecret1"},
    )
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
