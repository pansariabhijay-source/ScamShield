from __future__ import annotations

from app.detectors.base import DetectionContext
from app.detectors.impersonation_detector import ImpersonationDetector
from app.detectors.registry import get_ensemble
from app.detectors.text_detector import TextDetector
from app.detectors.upi_detector import UPIDetector
from app.detectors.url_detector import URLDetector
from app.models.enums import RiskLevel


def test_text_detector_flags_kyc_scam():
    det = TextDetector()
    ctx = DetectionContext(
        text="URGENT: Your KYC has expired. Update your PAN and share OTP or "
        "your account will be blocked immediately."
    )
    result = det.analyze(ctx)
    assert result.score > 0.6
    assert any("kyc" in s.code.lower() for s in result.signals)


def test_text_detector_safe_message():
    det = TextDetector()
    result = det.analyze(DetectionContext(text="Hey, are we still on for lunch tomorrow?"))
    assert result.score < 0.2


def test_url_detector_flags_ip_and_keywords():
    det = URLDetector()
    result = det.analyze(DetectionContext(url="http://192.168.1.10/secure-login-verify-bank"))
    assert result.score > 0.5
    codes = {s.code for s in result.signals}
    assert "url.ip_host" in codes


def test_url_detector_safe():
    det = URLDetector()
    result = det.analyze(DetectionContext(url="https://www.google.com"))
    assert result.score < 0.3


def test_upi_collect_request_is_high_risk():
    det = UPIDetector()
    ctx = DetectionContext(
        upi={
            "is_collect_request": True,
            "payee_vpa": "refund@randomhandle",
            "payee_name": "Cashback Reward",
            "amount": 1,
        }
    )
    result = det.analyze(ctx)
    assert result.score > 0.6


def test_impersonation_detector_freemail_bank():
    det = ImpersonationDetector()
    ctx = DetectionContext(
        text="Dear customer, your SBI account is blocked. Verify your netbanking password.",
        email_sender="alerts@gmail.com",
    )
    result = det.analyze(ctx)
    assert result.score > 0.5
    assert result.extra.get("institution") == "bank"


def test_ensemble_combines_to_scam():
    ensemble = get_ensemble()
    ctx = DetectionContext(
        text="Congratulations! You won a lottery. Pay processing fee via UPI now. "
        "Click http://claim-prize.tk/login and share your OTP urgently.",
        url="http://claim-prize.tk/login",
    )
    verdict = ensemble.run(ctx)
    assert verdict.risk_level in {RiskLevel.HIGH_RISK, RiskLevel.SCAM}
    assert 0 <= verdict.scam_probability <= 100
    assert verdict.reasons
    assert verdict.recommendation
