"""Seed reference data (scam categories) and an admin user.

Usage:  python -m scripts.seed
Idempotent — safe to run repeatedly.
"""
from __future__ import annotations

import os

from app.core.security import hash_password
from app.db.session import session_scope
from app.models.enums import UserRole
from app.models.scam_category import ScamCategory
from app.models.user import User
from app.repositories.user_repo import UserRepository

CATEGORIES = [
    ("kyc", "KYC Scam", "Fake account / KYC re-verification requests.",
     "Never share OTP/PAN. Verify only via your bank's official app."),
    ("lottery", "Lottery/Reward Scam", "Fake winnings requiring an upfront fee.",
     "Legitimate prizes never require advance payment."),
    ("investment", "Investment Scam", "Guaranteed/unrealistic returns.",
     "Be skeptical of guaranteed returns; verify SEBI registration."),
    ("job", "Job Scam", "Fake jobs charging registration fees.",
     "Real employers do not charge fees to hire you."),
    ("phishing", "Phishing / Credential Theft", "Steals login/card credentials.",
     "Do not enter credentials via links in messages."),
    ("impersonation", "Institution Impersonation", "Impersonates bank/RBI/govt.",
     "Contact the institution via official channels."),
    ("upi", "UPI/Payment Scam", "Collect-request and fake-payment frauds.",
     "Approving a collect request DEBITS you — never approve to 'receive'."),
]


def main() -> None:
    with session_scope() as db:
        for slug, name, desc, rec in CATEGORIES:
            exists = (
                db.query(ScamCategory).filter(ScamCategory.slug == slug).first()
            )
            if not exists:
                db.add(ScamCategory(slug=slug, name=name, description=desc,
                                    default_recommendation=rec))

        admin_email = os.getenv("ADMIN_EMAIL", "admin@scamshield.ai")
        repo = UserRepository(db)
        if not repo.get_by_email(admin_email):
            db.add(User(
                email=admin_email,
                hashed_password=hash_password(os.getenv("ADMIN_PASSWORD", "admin12345")),
                full_name="ScamShield Admin",
                role=UserRole.ADMIN,
                is_verified=True,
            ))
        print("Seed complete.")


if __name__ == "__main__":
    main()
