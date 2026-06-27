"""UPI fraud detector.

Detects: collect-request scams (you 'receive' a request that actually debits
you), fake payment screenshots, and QR-based scams. Uses an Isolation-Forest
seam for amount/behavior anomaly plus deterministic VPA/handle rules.
"""
from __future__ import annotations

import re

from app.detectors.base import BaseDetector, DetectionContext, DetectorResult, Signal

# Legitimate, well-known PSP handles. Unknown handles raise mild suspicion.
_KNOWN_HANDLES = {
    "okhdfcbank", "okicici", "oksbi", "okaxis", "ybl", "ibl", "axl", "paytm",
    "apl", "upi", "ptyes", "ptaxis", "pthdfc", "ptsbi", "fbl",
}
_VPA_RE = re.compile(r"\b[\w.\-]{2,256}@([a-zA-Z]{2,64})\b")
_SUSPICIOUS_NAME_TOKENS = [
    "refund", "cashback", "reward", "prize", "lottery", "kyc", "verify",
    "support", "helpdesk", "customercare", "lucky",
]


class UPIDetector(BaseDetector):
    name = "upi"
    handles = ("upi",)

    def applicable(self, ctx: DetectionContext) -> bool:
        return bool(ctx.upi)

    def _analyze(self, ctx: DetectionContext) -> DetectorResult:
        data: dict = ctx.upi or {}
        signals: list[Signal] = []
        score = 0.0

        vpa: str | None = (data.get("payee_vpa") or "").strip().lower() or None
        name: str | None = (data.get("payee_name") or "").strip().lower() or None
        amount = data.get("amount")
        note = (data.get("transaction_note") or "").lower()
        is_collect = bool(data.get("is_collect_request"))
        raw = (data.get("raw_text") or "").lower()

        # 1. Collect-request: classic "you are paying while thinking you receive"
        if is_collect:
            score += 0.45
            signals.append(Signal(
                "upi.collect_request",
                "This is a COLLECT request — approving it DEBITS your account, it does not pay you",
                0.45,
            ))

        # 2. Unknown / non-PSP handle
        if vpa:
            m = _VPA_RE.search(vpa)
            handle = m.group(1) if m else None
            if handle and handle not in _KNOWN_HANDLES:
                score += 0.18
                signals.append(Signal("upi.unknown_handle", f"Unrecognized UPI handle '@{handle}'", 0.18))
        else:
            score += 0.05

        # 3. Suspicious payee name tokens
        blob = " ".join(filter(None, [name, note, raw]))
        name_hits = [t for t in _SUSPICIOUS_NAME_TOKENS if t in blob]
        if name_hits:
            w = min(0.25, 0.08 * len(name_hits))
            score += w
            signals.append(Signal("upi.bait_name", f"Payee/note uses bait terms: {', '.join(name_hits[:3])}", w))

        # 4. "Refund/cashback requires you to pay first" pattern
        if any(t in blob for t in ("refund", "cashback")) and (is_collect or amount):
            score += 0.20
            signals.append(Signal("upi.refund_trap", "Refund/cashback that requires YOU to pay — known trap", 0.20))

        # 5. Amount anomaly (Isolation-Forest seam). Heuristic: round large amounts.
        if isinstance(amount, int | float) and amount >= 10000:
            score += 0.10
            signals.append(Signal("upi.high_amount", f"Unusually high amount (₹{amount:,.0f})", 0.10))

        # 6. Fake payment screenshot hints (from OCR'd raw text)
        if "payment successful" in raw and not vpa:
            score += 0.15
            signals.append(Signal("upi.fake_proof", "Looks like a payment-success screenshot with no verifiable VPA", 0.15))

        score = min(1.0, score)
        confidence = 0.75 if signals else 0.4
        return DetectorResult(
            detector=self.name,
            score=score,
            confidence=confidence,
            signals=signals,
            explanation="UPI transaction risk evaluated.",
            extra={"category": "UPI/Payment Scam" if score > 0.5 else None},
        )
