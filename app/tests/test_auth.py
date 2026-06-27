from __future__ import annotations


def test_register_and_login(client):
    r = client.post(
        "/api/v1/auth/register",
        json={"email": "a@b.com", "password": "password123", "full_name": "A B"},
    )
    assert r.status_code == 201, r.text
    assert r.json()["email"] == "a@b.com"

    r = client.post("/api/v1/auth/login", json={"email": "a@b.com", "password": "password123"})
    assert r.status_code == 200
    body = r.json()
    assert body["access_token"] and body["refresh_token"]


def test_duplicate_registration_conflicts(client):
    payload = {"email": "dup@b.com", "password": "password123"}
    assert client.post("/api/v1/auth/register", json=payload).status_code == 201
    assert client.post("/api/v1/auth/register", json=payload).status_code == 409


def test_login_wrong_password(client):
    client.post("/api/v1/auth/register", json={"email": "c@b.com", "password": "password123"})
    r = client.post("/api/v1/auth/login", json={"email": "c@b.com", "password": "wrong"})
    assert r.status_code == 401


def test_refresh_flow(client):
    client.post("/api/v1/auth/register", json={"email": "d@b.com", "password": "password123"})
    tokens = client.post("/api/v1/auth/login", json={"email": "d@b.com", "password": "password123"}).json()
    r = client.post("/api/v1/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert r.status_code == 200
    assert r.json()["access_token"]


def test_protected_route_requires_auth(client):
    assert client.get("/api/v1/history").status_code == 401
