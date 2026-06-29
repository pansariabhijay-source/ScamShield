"""Shared text normalization for the NLP classifier.

Used as the TfidfVectorizer ``preprocessor`` so it is *baked into* the serialized
model — guaranteeing identical preprocessing at train time and serve time (the
classic source of train/serve skew).

Why normalize: raw scam/ham text is full of high-cardinality tokens (specific
amounts, phone numbers, OTP codes, URLs, years) that the model would otherwise
memorize — learning spurious things like "2001 ⇒ ham" (an Enron artifact) or a
particular ₹ amount. Collapsing each class to a single placeholder lets the model
learn the *structure* of a scam ("_amount_ will be debited", "verify _url_") and
generalize far better to messages it has never seen.
"""
from __future__ import annotations

import re

# Order matters: URLs/emails first (they contain dots & digits), then currency
# amounts (before bare numbers so "Rs 239.88" → _amount_, not _num_), then phone
# numbers, masked numbers, and finally any remaining digit runs.
_URL = re.compile(
    r"(?:https?://|www\.)\S+"
    r"|\b[a-z0-9](?:[a-z0-9-]*[a-z0-9])?(?:\.[a-z0-9-]+)*\."
    r"(?:com|in|co|net|org|io|me|info|xyz|top|link|ly|gd|to|app|gov|edu|biz|online|site)"
    r"(?:/\S*)?",
    re.IGNORECASE,
)
_EMAIL = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b")
_AMOUNT = re.compile(r"(?:rs\.?|inr|₹|usd|\$|£)\s?\d[\d,]*(?:\.\d+)?", re.IGNORECASE)
_PHONE = re.compile(r"\b(?:\+?91[-\s]?)?[6-9]\d{9}\b")
_MASKED = re.compile(r"\b(?=[\dxX*]*[xX*])(?=[\dxX*]*\d)[\dxX*]{5,}\b")  # 72188XXXXX, xx1234
_NUM = re.compile(r"\b\d{3,}\b")  # OTPs, codes, years, account fragments


def normalize(text: str) -> str:
    t = (text or "").lower()
    t = _URL.sub(" _url_ ", t)
    t = _EMAIL.sub(" _email_ ", t)
    t = _AMOUNT.sub(" _amount_ ", t)
    t = _PHONE.sub(" _phone_ ", t)
    t = _MASKED.sub(" _num_ ", t)
    t = _NUM.sub(" _num_ ", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t
