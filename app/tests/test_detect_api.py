from __future__ import annotations


def test_detect_text_endpoint(client, auth_headers):
    r = client.post(
        "/api/v1/detect/text",
        headers=auth_headers,
        json={
            "content": "URGENT! Your KYC expired. Share OTP and click http://bit.ly/x now or account blocked.",
            "input_type": "SMS",
        },
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert 0 <= body["scam_probability"] <= 100
    assert body["risk_level"] in {"SAFE", "SUSPICIOUS", "HIGH_RISK", "SCAM"}
    assert body["reasons"]
    assert body["recommendation"]
    assert body["scan_id"]


def test_detect_url_endpoint(client, auth_headers):
    r = client.post(
        "/api/v1/detect/url",
        headers=auth_headers,
        json={"url": "http://secure-login-verify.tk/bank"},
    )
    assert r.status_code == 200
    assert r.json()["risk_level"] in {"SUSPICIOUS", "HIGH_RISK", "SCAM"}


def test_detect_upi_collect(client, auth_headers):
    r = client.post(
        "/api/v1/detect/upi",
        headers=auth_headers,
        json={
            "payee_vpa": "refund@xyz",
            "payee_name": "Cashback",
            "is_collect_request": True,
            "amount": 1,
        },
    )
    assert r.status_code == 200
    assert r.json()["scam_probability"] >= 30


def test_history_roundtrip(client, auth_headers):
    client.post(
        "/api/v1/detect/text",
        headers=auth_headers,
        json={"content": "hello friend lunch tomorrow?"},
    )
    lst = client.get("/api/v1/history", headers=auth_headers)
    assert lst.status_code == 200
    data = lst.json()
    assert data["total"] >= 1
    scan_id = data["items"][0]["id"]

    detail = client.get(f"/api/v1/history/{scan_id}", headers=auth_headers)
    assert detail.status_code == 200
    assert detail.json()["scan_id"] == scan_id


def test_health_and_ready(client):
    assert client.get("/health").status_code == 200
    assert client.get("/ready").status_code == 200
