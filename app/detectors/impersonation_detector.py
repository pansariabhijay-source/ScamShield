"""Institution impersonation detector.

Flags content that *claims* to be from a trusted institution (bank, RBI, income
tax, courier, telecom) while exhibiting impostor tells: free-mail senders,
look-alike domains, mismatched sender vs. claimed brand, and brand + credential
asks. Embedding-similarity is the upgrade path; MVP uses brand lexicons.
"""
from __future__ import annotations

import re

from app.detectors.base import BaseDetector, DetectionContext, DetectorResult, Signal

_INSTITUTIONS: dict[str, list[str]] = {
    "bank": ["sbi", "state bank", "hdfc", "icici", "axis bank", "kotak", "punjab national", "pnb", "bank of baroda"],
    "rbi": ["rbi", "reserve bank"],
    "income_tax": ["income tax", "incometax", "it department", "tds", "refund department"],
    "courier": ["fedex", "dhl", "bluedart", "dtdc", "india post", "customs", "parcel"],
    "telecom": ["jio", "airtel", "vodafone", "vi ", "bsnl", "trai"],
    "wallet": ["paytm", "phonepe", "google pay", "gpay", "amazon pay"],
}
_FREEMAIL = {"gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "rediffmail.com", "proton.me"}
_OFFICIAL_DOMAINS = {
    "bank": ["sbi.co.in", "hdfcbank.com", "icicibank.com", "axisbank.com"],
    "rbi": ["rbi.org.in"],
    "income_tax": ["incometax.gov.in", "incometaxindia.gov.in"],
    "telecom": ["jio.com", "airtel.in", "trai.gov.in"],
}
_CRED_ASK = re.compile(
    r"\b(otp|cvv|pin|password|card number|aadhaar|pan|expiry)\b", re.I
)
# "do NOT share your OTP" is a legitimate-sender advisory, not an impostor ask.
_NEG_SHARE = re.compile(
    r"\b(do not|don'?t|never|please do not)\s+(share|disclose|reveal|give|provide|tell)\b",
    re.I,
)


class ImpersonationDetector(BaseDetector):
    name = "impersonation"
    handles = ("text", "email_sender")

    def _analyze(self, ctx: DetectionContext) -> DetectorResult:
        text = (ctx.text or "").lower()
        sender = (ctx.email_sender or "").lower()
        if not text and not sender:
            return DetectorResult(detector=self.name, score=0.0, confidence=0.0)

        signals: list[Signal] = []
        score = 0.0
        claimed: str | None = None

        for inst, tokens in _INSTITUTIONS.items():
            if any(t in text or t in sender for t in tokens):
                claimed = inst
                break

        if not claimed:
            return DetectorResult(
                detector=self.name, score=0.0, confidence=0.4,
                explanation="No institution impersonation detected.",
            )

        score += 0.15
        signals.append(Signal("imp.claims_institution", f"Content claims to be from a {claimed.replace('_', ' ')}", 0.15))

        # Sender-domain analysis (email path)
        domain = sender.split("@")[-1] if "@" in sender else ""
        if domain:
            if domain in _FREEMAIL:
                score += 0.30
                signals.append(Signal("imp.freemail_sender",
                                      f"A real {claimed} never emails from a free address ({domain})", 0.30))
            else:
                official = _OFFICIAL_DOMAINS.get(claimed, [])
                if official and not any(domain.endswith(o) for o in official):
                    score += 0.25
                    signals.append(Signal("imp.lookalike_domain",
                                          f"Sender domain '{domain}' is not an official {claimed} domain", 0.25))

        # Brand + credential ask is the strongest impostor tell — but only when
        # the message actually solicits the secret, not when it merely warns
        # "never share your OTP" (the hallmark of a genuine bank notification).
        if _CRED_ASK.search(text) and not _NEG_SHARE.search(text):
            score += 0.30
            signals.append(Signal("imp.cred_request",
                                  f"Asks for sensitive credentials while posing as {claimed}", 0.30))

        score = min(1.0, score)
        label = {
            "bank": "Bank Impersonation Scam",
            "rbi": "RBI Impersonation Scam",
            "income_tax": "Income Tax Scam",
            "courier": "Courier/Parcel Scam",
            "telecom": "Telecom (KYC) Scam",
            "wallet": "Wallet Impersonation Scam",
        }.get(claimed)
        return DetectorResult(
            detector=self.name,
            score=score,
            confidence=0.8,
            signals=signals,
            explanation=f"Possible impersonation of {claimed}.",
            extra={"institution": claimed, "category": label},
        )
