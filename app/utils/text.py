from __future__ import annotations

import re

_WS = re.compile(r"\s+")
_URL = re.compile(r"https?://[^\s]+", re.IGNORECASE)


def normalize(text: str) -> str:
    return _WS.sub(" ", text or "").strip()


def extract_urls(text: str) -> list[str]:
    return _URL.findall(text or "")


def truncate(text: str, limit: int = 280) -> str:
    text = text or ""
    return text if len(text) <= limit else text[: limit - 1] + "…"
