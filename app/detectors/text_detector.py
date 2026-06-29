"""NLP scam classifier.

MVP implementation = weighted lexicon + pattern features producing a calibrated
score. The class is structured exactly like a model wrapper: `_featurize` ->
`_score`. To upgrade, set `ENABLE_HEAVY_MODELS=True` and implement
`_score_with_model` using DistilBERT/MiniLM — the rest of the system is unchanged.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from app.core.config import settings
from app.core.logging import get_logger
from app.detectors.base import BaseDetector, DetectionContext, DetectorResult, Signal

logger = get_logger("scamshield.text")

_MODEL_DIR = Path(__file__).resolve().parent / "models"
_MODEL_PATH = _MODEL_DIR / "text_clf.joblib"
_META_PATH = _MODEL_DIR / "text_clf.meta.json"

# Category -> (regex patterns, weight). Patterns compiled once at import.
_CATEGORY_PATTERNS: dict[str, tuple[list[str], float]] = {
    "urgency": (
        [r"\burgent(ly)?\b", r"\bimmediate(ly)?\b", r"\bact now\b", r"\bwithin \d+ ?(hours|hrs|minutes)\b",
         r"\bexpir(e|es|ing|ed)\b", r"\block(ed|ing)?\b", r"\bsuspend(ed)?\b", r"\blast warning\b"],
        0.18,
    ),
    "threat": (
        [r"\blegal action\b", r"\barrest\b", r"\bpenalt(y|ies)\b", r"\bfine\b",
         r"\bcourt\b", r"\bblock(ed)? your account\b", r"\bpolice\b"],
        0.20,
    ),
    "kyc": (
        [r"\bkyc\b", r"\bre-?verif(y|ication)\b", r"\bupdate your (pan|aadhaar|aadhar|details)\b",
         r"\bpan card\b", r"\baadhaar\b", r"\baccount will be (blocked|suspended)\b"],
        0.22,
    ),
    "reward_lottery": (
        [r"\bcongratulat(e|ions)\b", r"\byou have won\b", r"\blottery\b", r"\bprize\b",
         r"\bclaim your (reward|prize|gift)\b", r"\bfree\b.*\b(gift|cash|recharge)\b", r"\blucky (draw|winner)\b"],
        0.18,
    ),
    "investment": (
        [r"\bguaranteed returns?\b", r"\bdouble your (money|investment)\b", r"\bhigh returns?\b",
         r"\binvest(ment)? opportunity\b", r"\bcrypto\b.*\bprofit\b", r"\b\d+%\s*(daily|monthly|returns?)\b"],
        0.20,
    ),
    "job": (
        [r"\bwork from home\b", r"\bpart[- ]time job\b", r"\bearn \$?₹?\d+ ?(per day|daily|weekly)\b",
         r"\bno experience (needed|required)\b", r"\bregistration fee\b", r"\bhiring\b.*\bwhatsapp\b"],
        0.16,
    ),
    # The scam tell is being *asked* to hand over a secret — not the mere mention
    # of one. Legit bank/delivery notices say "your OTP is ..."; phishing says
    # "share your OTP". Splitting these keeps genuine notifications from scoring
    # like attacks. ("netbanking" is a channel, not a secret — excluded.)
    "credentials_ask": (
        [r"\b(share|send|give|provide|enter|confirm|tell us)\b.{0,20}\b(otp|pin|cvv|password|card number|one[- ]time password)\b",
         r"\b(otp|pin|cvv|password)\b.{0,15}\b(immediately|now|urgent|to (verify|confirm|continue))\b"],
        0.24,
    ),
    "credentials_mention": (
        [r"\bone[- ]time password\b", r"\botp\b", r"\bcvv\b", r"\bpin\b",
         r"\bpassword\b", r"\bcard number\b"],
        0.08,
    ),
    "impersonation_hint": (
        [r"\bdear customer\b", r"\bofficial\b", r"\bverification (team|department)\b",
         r"\bcustomer (care|support)\b.*\b(call|sms)\b"],
        0.08,
    ),
    "money_request": (
        [r"\bsend money\b", r"\btransfer\b.*\b(now|immediately)\b", r"\bpay\b.*\bfee\b",
         r"\bupi\b", r"\bgoogle ?pay\b", r"\bphonepe\b", r"\bpaytm\b", r"\bscan (this )?qr\b",
         r"\b(clearance|customs|processing|registration|delivery) (fee|charge|duty)\b",
         r"\bpay\b.*\b(clearance|customs|to (release|claim))\b"],
        0.14,
    ),
}

_COMPILED = {
    cat: ([re.compile(p, re.IGNORECASE) for p in pats], w)
    for cat, (pats, w) in _CATEGORY_PATTERNS.items()
}

# Negated credential phrasing ("do NOT share your OTP") is the hallmark of a
# *legitimate* bank/transaction message, not a phishing ask. Used to neutralise
# the credentials signal so genuine OTP/PIN notifications aren't flagged.
_NEG_SHARE = re.compile(
    r"\b(do not|don'?t|never|do not ever|please do not)\s+"
    r"(share|disclose|reveal|give|provide|tell)\b",
    re.IGNORECASE,
)

# UPI "collect" / request-money phrasing. Telling the user that approving such a
# request DEBITS them (rather than pays them) is the single most useful thing we
# can surface — true whether the request is legitimate or fraudulent.
_COLLECT_LANGUAGE = re.compile(
    r"\b(requested money from you|has requested|collect request|payment request|"
    r"requesting (?:rs|₹|inr|payment)|will be debited from your account|"
    r"on approving (?:the |this )?request|approve (?:the |this )?request)\b",
    re.IGNORECASE,
)

# Map internal feature categories to user-facing scam categories.
_CATEGORY_LABELS = {
    "kyc": "KYC Scam",
    "reward_lottery": "Lottery/Reward Scam",
    "investment": "Investment Scam",
    "job": "Job Scam",
    "credentials_ask": "Phishing / Credential Theft",
    "threat": "Extortion / Threat Scam",
}


class TextDetector(BaseDetector):
    name = "text"
    handles = ("text",)

    def __init__(self) -> None:
        self._model = None  # optional heavy transformer (ENABLE_HEAVY_MODELS)
        self._clf = None  # trained lightweight sklearn pipeline (default path)
        self._clf_version: str | None = None
        self._load_sklearn_model()
        if settings.ENABLE_HEAVY_MODELS:
            self._try_load_model()

    def _load_sklearn_model(self) -> None:
        """Load the TF-IDF + LogisticRegression model trained on real corpora.

        Trained by `scripts/train_text_model.py`; ships as a ~1.5 MB joblib so it
        loads instantly and runs sub-ms on CPU. Absence is non-fatal — the engine
        degrades gracefully to the heuristic lexicon scorer.
        """
        try:
            import joblib

            if _MODEL_PATH.exists():
                self._clf = joblib.load(_MODEL_PATH)
                if _META_PATH.exists():
                    self._clf_version = json.loads(_META_PATH.read_text()).get("version")
                logger.info("text_model_loaded", extra={"version": self._clf_version})
        except Exception as exc:
            logger.warning("text_model_load_failed", extra={"error": str(exc)})
            self._clf = None

    def _try_load_model(self) -> None:  # pragma: no cover - heavy path
        try:
            from transformers import pipeline

            self._model = pipeline(
                "text-classification", model=settings.NLP_MODEL_NAME, top_k=None
            )
        except Exception:
            self._model = None  # fall back to heuristics

    def _featurize(self, text: str) -> dict[str, float]:
        hits: dict[str, float] = {}
        for cat, (patterns, weight) in _COMPILED.items():
            matched = sum(1 for p in patterns if p.search(text))
            if matched:
                # The presence of a *category* is the primary evidence; extra
                # synonym hits within the same category add a small, saturating
                # bonus (1 hit -> w, 2 -> 1.35w, 3+ -> 1.7w). Cross-category
                # accumulation (urgency + threat + credentials ...) is what
                # drives a message toward a confident scam verdict.
                hits[cat] = weight * (1.0 + 0.35 * min(matched - 1, 2))

        # A genuine "do not share your OTP/PIN" advisory is legitimate, not a
        # credential-harvesting ask — heavily discount any credential signal.
        if _NEG_SHARE.search(text):
            for k in ("credentials_ask", "credentials_mention"):
                if k in hits:
                    hits[k] *= 0.2
        return hits

    def _analyze(self, ctx: DetectionContext) -> DetectorResult:
        text = (ctx.text or "").strip()
        if not text:
            return DetectorResult(detector=self.name, score=0.0, confidence=0.0)

        # Heuristic lexicon always runs: it supplies the human-readable category
        # and explainable per-pattern signals regardless of which scorer is used.
        features = self._featurize(text)
        signals: list[Signal] = [
            Signal(code=f"text.{cat}", description=_human(cat), weight=round(val, 3))
            for cat, val in sorted(features.items(), key=lambda x: -x[1])
        ]
        dominant = max(features, key=features.get) if features else None
        category = _CATEGORY_LABELS.get(dominant) if dominant else None

        # Heuristic score (fallback / blend partner). Calibrated (k=2.7) so a
        # single category lands ~0.4 and several converging categories exceed 0.7.
        raw = sum(features.values())
        heuristic = 1 - pow(2.718281828, -2.7 * raw)

        # Primary scorer: the model trained on ~34k real scam/spam messages.
        if self._clf is not None:
            proba = float(self._clf.predict_proba([text])[0][1])
            # Trust-aware fusion of the data-trained model and the hand-tuned
            # heuristic:
            #  * heuristic confident (>=0.5): it was tuned for exactly these
            #    region-specific scams (extortion/KYC/UPI) that are rare in the
            #    training corpus — let it ESCALATE via max().
            #  * otherwise: the data model leads but is DAMPED by a blend, so its
            #    out-of-distribution false positives (legit OTP/transactional SMS
            #    that look spammy) can't fire on their own.
            if heuristic >= 0.5:
                score = max(proba, heuristic)
            else:
                score = 0.6 * proba + 0.4 * heuristic
            # Legitimacy override: an explicit "do not share your OTP/PIN" advisory
            # with no credential *ask* is the signature of a genuine bank/delivery
            # notification — cap it well below the alert threshold.
            if _NEG_SHARE.search(text) and "credentials_ask" not in features:
                score = min(score, 0.35)
            confidence = round(0.72 + 0.27 * abs(2 * proba - 1), 3)  # 0.72‑0.99

            # Most useful concrete reason for a UPI pull request, legit or not.
            if _COLLECT_LANGUAGE.search(text):
                signals.append(Signal(
                    "text.collect_request",
                    "This is a ‘request money’ / UPI collect message — approving it "
                    "DEBITS your account. Only approve if you meant to pay them.",
                    0.5,
                ))

            # Honest, human reason — never a bare circular "the model says X%", and
            # never claim "resembles scam" on a message we're calling safe.
            if features:
                ml_reason = "Message wording matches known scam patterns"
                ml_weight = round(proba, 3)
            elif proba >= 0.65:
                ml_reason = "Writing style resembles known scam/spam messages — verify the sender"
                ml_weight = round(proba, 3)
                confidence = round(confidence * 0.7, 3)  # unexplained => less sure
            else:
                ml_reason = "No specific scam wording detected"
                ml_weight = 0.05
            signals.append(Signal("text.ml", ml_reason, ml_weight))
            explanation = ml_reason + ("; " + _explain(features).lower() if features else ".")
            return DetectorResult(
                detector=self.name, score=score, confidence=confidence, signals=signals,
                explanation=explanation,
                extra={"category": category, "features": features,
                       "ml_proba": round(proba, 4), "model_version": self._clf_version},
            )

        if self._model is not None:  # pragma: no cover - heavy transformer path
            return self._score_with_model(text)

        # confidence grows with text length and number of distinct signals
        confidence = min(0.95, 0.4 + 0.1 * len(features) + min(len(text), 500) / 2500)
        return DetectorResult(
            detector=self.name,
            score=heuristic,
            confidence=confidence,
            signals=signals,
            explanation=_explain(features),
            extra={"category": category, "features": features},
        )

    def _score_with_model(self, text: str) -> DetectorResult:  # pragma: no cover
        preds = self._model(text)[0]
        scam = next((p["score"] for p in preds if p["label"].upper() in {"SCAM", "LABEL_1"}), 0.0)
        return DetectorResult(
            detector=self.name, score=scam, confidence=0.8,
            explanation="Transformer classifier", extra={"raw": preds},
        )


def _human(cat: str) -> str:
    return {
        "urgency": "Urgency / pressure language detected",
        "threat": "Threatening or coercive language",
        "kyc": "KYC / account-verification lure",
        "reward_lottery": "Reward, prize or lottery bait",
        "investment": "Unrealistic investment / returns promise",
        "job": "Suspicious job / earning offer",
        "credentials_ask": "Requests sensitive credentials (OTP/PIN/CVV/password)",
        "credentials_mention": "Mentions credentials (OTP/PIN/CVV)",
        "impersonation_hint": "Generic official-sounding language",
        "money_request": "Requests money transfer / payment",
    }.get(cat, cat)


def _explain(features: dict[str, float]) -> str:
    if not features:
        return "No strong scam indicators in text."
    top = sorted(features, key=features.get, reverse=True)[:3]
    return "Detected: " + ", ".join(_human(c) for c in top)
