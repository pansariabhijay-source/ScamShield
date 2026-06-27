"""NLP scam classifier.

MVP implementation = weighted lexicon + pattern features producing a calibrated
score. The class is structured exactly like a model wrapper: `_featurize` ->
`_score`. To upgrade, set `ENABLE_HEAVY_MODELS=True` and implement
`_score_with_model` using DistilBERT/MiniLM — the rest of the system is unchanged.
"""
from __future__ import annotations

import re

from app.core.config import settings
from app.detectors.base import BaseDetector, DetectionContext, DetectorResult, Signal

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
    "credentials": (
        [r"\bone[- ]time password\b", r"\botp\b", r"\bcvv\b", r"\bpin\b", r"\bpassword\b",
         r"\bnet ?banking\b", r"\bcard number\b", r"\bshare (your )?(otp|pin|cvv)\b"],
        0.24,
    ),
    "impersonation_hint": (
        [r"\bdear customer\b", r"\bofficial\b", r"\bverification (team|department)\b",
         r"\bcustomer (care|support)\b.*\b(call|sms)\b"],
        0.08,
    ),
    "money_request": (
        [r"\bsend money\b", r"\btransfer\b.*\b(now|immediately)\b", r"\bpay\b.*\bfee\b",
         r"\bupi\b", r"\bgoogle ?pay\b", r"\bphonepe\b", r"\bpaytm\b", r"\bscan (this )?qr\b"],
        0.14,
    ),
}

_COMPILED = {
    cat: ([re.compile(p, re.IGNORECASE) for p in pats], w)
    for cat, (pats, w) in _CATEGORY_PATTERNS.items()
}

# Map internal feature categories to user-facing scam categories.
_CATEGORY_LABELS = {
    "kyc": "KYC Scam",
    "reward_lottery": "Lottery/Reward Scam",
    "investment": "Investment Scam",
    "job": "Job Scam",
    "credentials": "Phishing / Credential Theft",
    "threat": "Extortion / Threat Scam",
}


class TextDetector(BaseDetector):
    name = "text"
    handles = ("text",)

    def __init__(self) -> None:
        self._model = None
        if settings.ENABLE_HEAVY_MODELS:
            self._try_load_model()

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
                # diminishing returns: 1 - exp(-k) style via simple cap
                hits[cat] = weight * min(matched, 3) / 3 + weight * 0.5 * (matched > 0)
        return hits

    def _analyze(self, ctx: DetectionContext) -> DetectorResult:
        text = (ctx.text or "").strip()
        if not text:
            return DetectorResult(detector=self.name, score=0.0, confidence=0.0)

        if self._model is not None:  # pragma: no cover
            return self._score_with_model(text)

        features = self._featurize(text)
        raw = sum(features.values())
        # squashing keeps score in (0,1); 0.9 calibration so ~4 strong signals -> high
        score = 1 - pow(2.718281828, -1.1 * raw)

        signals: list[Signal] = []
        for cat, val in sorted(features.items(), key=lambda x: -x[1]):
            signals.append(
                Signal(code=f"text.{cat}", description=_human(cat), weight=round(val, 3))
            )

        # confidence grows with text length and number of distinct signals
        confidence = min(0.95, 0.4 + 0.1 * len(features) + min(len(text), 500) / 2500)

        dominant = max(features, key=features.get) if features else None
        category = _CATEGORY_LABELS.get(dominant) if dominant else None

        return DetectorResult(
            detector=self.name,
            score=score,
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
        "credentials": "Requests sensitive credentials (OTP/PIN/CVV)",
        "impersonation_hint": "Generic official-sounding language",
        "money_request": "Requests money transfer / payment",
    }.get(cat, cat)


def _explain(features: dict[str, float]) -> str:
    if not features:
        return "No strong scam indicators in text."
    top = sorted(features, key=features.get, reverse=True)[:3]
    return "Detected: " + ", ".join(_human(c) for c in top)
