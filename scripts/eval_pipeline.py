"""Offline accuracy benchmark for the detection ensemble.

Runs a labeled corpus of scam / legitimate ("ham") inputs through the live
ensemble and reports confusion matrix, precision/recall/F1 and the specific
misclassified cases. Use it to tune detectors & weights against numbers instead
of vibes:  `python -m scripts.eval_pipeline`
"""
from __future__ import annotations

from dataclasses import dataclass

from app.detectors.base import DetectionContext
from app.detectors.registry import get_ensemble

# Decision threshold on the 0-100 scam_probability: >= FLAG_AT => "scam".
FLAG_AT = 50


@dataclass
class Case:
    label: int  # 1 = scam, 0 = legitimate
    ctx: DetectionContext
    note: str


def C(label, note, **kw):
    return Case(label=label, ctx=DetectionContext(**kw), note=note)


CASES: list[Case] = [
    # ---------------- SCAMS (label=1) ----------------
    C(1, "kyc-otp", text="URGENT: Your KYC has expired. Update your PAN and share OTP now or your account will be blocked immediately."),
    C(1, "lottery", text="Congratulations! You have won a lottery of Rs 25,00,000. Pay a small processing fee to claim your prize now."),
    C(1, "investment", text="Double your money in 30 days! Guaranteed returns of 10% daily. Invest now, limited slots."),
    C(1, "job", text="Work from home job! Earn ₹5000 per day, no experience needed. Pay registration fee on WhatsApp to start."),
    C(1, "phishing-link", text="Your account is suspended. Verify immediately: http://sbi-secure-verify.tk/login", url="http://sbi-secure-verify.tk/login"),
    C(1, "bank-impersonation", text="Dear customer, your SBI account is blocked. Verify your netbanking password to reactivate.", email_sender="alerts@gmail.com"),
    C(1, "extortion", text="This is the police. A case has been filed against you. Pay the fine immediately to avoid arrest."),
    C(1, "courier", text="Your FedEx parcel is held at customs. Pay ₹250 clearance fee here: http://fedex-india-customs.xyz/pay", url="http://fedex-india-customs.xyz/pay"),
    C(1, "refund-trap", text="Income Tax refund of ₹15,400 approved. Confirm your account and share OTP to receive it."),
    C(1, "upi-collect", upi={"is_collect_request": True, "payee_vpa": "refund@randomhandle", "payee_name": "Cashback Reward", "amount": 1}),
    C(1, "ip-url", url="http://192.168.1.10/secure-login-verify-bank-account"),
    C(1, "shortener-phish", text="Claim your free gift: https://bit.ly/free-prize-now", url="https://bit.ly/free-prize-now"),
    C(1, "punycode", url="https://xn--paypa-9db.com/login"),
    C(1, "telecom-kyc", text="Your mobile number will be disconnected today. Complete KYC verification urgently by clicking the link."),
    C(1, "crypto", text="Exclusive crypto investment opportunity. High returns guaranteed, double your investment in a week."),

    # ---------------- LEGITIMATE / HAM (label=0) ----------------
    C(0, "lunch", text="Hey, are we still on for lunch tomorrow?"),
    C(0, "legit-otp", text="Your OTP is 459123. Do not share it with anyone. - HDFC Bank"),
    C(0, "order-shipped", text="Your Amazon order has shipped and will arrive Friday. Track it in the Orders section."),
    C(0, "bill-reminder", text="Reminder: your electricity bill of Rs 1,240 is due on 5th. Pay via the BESCOM app."),
    C(0, "netbanking-legit", text="Your account statement for June is ready. Login at https://netbanking.hdfcbank.com to view.", url="https://netbanking.hdfcbank.com"),
    C(0, "meeting", text="The team meeting is moved to 3 PM. Please update your calendar."),
    C(0, "google", url="https://www.google.com"),
    C(0, "github", url="https://github.com/anthropics/anthropic-sdk-python"),
    C(0, "newsletter", text="Thanks for subscribing! Here is your weekly roundup of articles. Unsubscribe anytime."),
    C(0, "delivery-otp", text="Your delivery OTP is 8842. Share it with the delivery agent on arrival."),
    C(0, "salary", text="Your salary for this month has been credited to your account. View details in the app."),
    C(0, "appointment", text="Your doctor appointment is confirmed for Monday 10 AM. Reply to reschedule."),
    C(0, "movie", text="Booking confirmed! Your tickets for the 7 PM show are ready. Enjoy the movie."),
    C(0, "support-legit", url="https://support.microsoft.com/en-us/account"),
    C(0, "flight", text="Web check-in is now open for your flight. Visit the airline app to select seats."),
]


def main() -> None:
    ensemble = get_ensemble()
    tp = fp = tn = fn = 0
    errors: list[str] = []

    for case in CASES:
        verdict = ensemble.run(case.ctx)
        pred = 1 if verdict.scam_probability >= FLAG_AT else 0
        if case.label == 1 and pred == 1:
            tp += 1
        elif case.label == 1 and pred == 0:
            fn += 1
            errors.append(f"  MISS  (FN) {case.note:<20} p={verdict.scam_probability:>3} {verdict.risk_level.value}")
        elif case.label == 0 and pred == 1:
            fp += 1
            errors.append(f"  FALSE (FP) {case.note:<20} p={verdict.scam_probability:>3} {verdict.risk_level.value}")
        else:
            tn += 1

    total = len(CASES)
    acc = (tp + tn) / total
    prec = tp / (tp + fp) if (tp + fp) else 0.0
    rec = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) else 0.0

    print(f"\n=== ScamShield ensemble benchmark (threshold>={FLAG_AT}) ===")
    print(f"cases={total}  TP={tp} FP={fp} TN={tn} FN={fn}")
    print(f"accuracy={acc:.3f}  precision={prec:.3f}  recall={rec:.3f}  f1={f1:.3f}")
    if errors:
        print("\nMisclassified:")
        print("\n".join(errors))
    else:
        print("\nAll cases classified correctly.")


if __name__ == "__main__":
    main()
