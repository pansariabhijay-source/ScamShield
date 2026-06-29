"""URL reputation engine.

Computes lexical + structural features (entropy, TLD risk, shortener, phishing
keywords, IP-as-host, punycode, excessive subdomains). These are exactly the
features fed to a gradient-boosted model (XGBoost) in production; here we apply
a transparent rule-weighted scorer behind the same interface.
"""
from __future__ import annotations

import math
import re
from collections import Counter
from urllib.parse import urlparse

from app.detectors.base import BaseDetector, DetectionContext, DetectorResult, Signal

_SUSPICIOUS_TLDS = {
    "zip", "mov", "xyz", "top", "club", "click", "country", "stream", "gq", "tk",
    "ml", "cf", "ga", "work", "loan", "rest", "fit", "men", "date", "review",
}
_SHORTENERS = {
    "bit.ly", "tinyurl.com", "goo.gl", "t.co", "ow.ly", "is.gd", "buff.ly",
    "rb.gy", "cutt.ly", "shorturl.at", "rebrand.ly",
}
_PHISH_KEYWORDS = [
    "login", "verify", "secure", "account", "update", "bank", "kyc", "wallet",
    "confirm", "signin", "password", "free", "gift", "bonus", "claim", "paytm",
    "refund", "netbanking", "support", "customs", "parcel", "prize", "reward",
]
_BRAND_TOKENS = [
    "sbi", "hdfc", "icici", "axis", "paypal", "amazon", "flipkart", "netflix",
    "whatsapp", "instagram", "rbi", "incometax", "irctc",
    "fedex", "dhl", "dtdc", "bluedart",
]
# Registrable domains we trust. A host on (or under) one of these is treated as
# legitimate: brand/keyword heuristics that exist to catch *impostor* domains
# would otherwise fire on the real site (e.g. netbanking.hdfcbank.com) and
# generate false positives. Matched as an exact-or-subdomain suffix.
_TRUSTED_DOMAINS = {
    "google.com", "youtube.com", "github.com", "microsoft.com", "apple.com",
    "amazon.com", "amazon.in", "flipkart.com", "netflix.com", "paypal.com",
    "whatsapp.com", "instagram.com", "facebook.com", "linkedin.com",
    "sbi.co.in", "onlinesbi.sbi", "hdfcbank.com", "icicibank.com",
    "axisbank.com", "kotak.com", "rbi.org.in", "incometax.gov.in",
    "irctc.co.in", "jio.com", "airtel.in", "uidai.gov.in", "gov.in",
}


def _is_trusted(host: str) -> bool:
    return any(host == d or host.endswith("." + d) for d in _TRUSTED_DOMAINS)


def _shannon_entropy(s: str) -> float:
    if not s:
        return 0.0
    counts = Counter(s)
    n = len(s)
    return -sum((c / n) * math.log2(c / n) for c in counts.values())


class URLDetector(BaseDetector):
    name = "url"
    handles = ("url",)

    def _analyze(self, ctx: DetectionContext) -> DetectorResult:
        url = (ctx.url or "").strip()
        if not url:
            return DetectorResult(detector=self.name, score=0.0, confidence=0.0)
        # A scheme the user didn't type tells us nothing about security. Only
        # judge HTTPS when an explicit scheme was actually present in the input.
        scheme_provided = "://" in url
        if not scheme_provided:
            url = "http://" + url

        parsed = urlparse(url)
        host = (parsed.hostname or "").lower()
        signals: list[Signal] = []
        score = 0.0

        # 0. Trusted, well-known destination — short-circuit as legitimate so the
        # impostor-oriented heuristics below don't penalise the real brand site.
        if _is_trusted(host):
            return DetectorResult(
                detector=self.name,
                score=0.0,
                confidence=0.85,
                signals=[Signal("url.trusted", f"Recognised official domain '{host}'", 0.0)],
                explanation=f"'{host}' is a recognised, trusted domain.",
                extra={"host": host, "trusted": True},
            )

        # 1. No HTTPS — only meaningful if the sender actually wrote "http://".
        if scheme_provided and parsed.scheme != "https":
            score += 0.10
            signals.append(Signal("url.no_https", "Link explicitly uses insecure HTTP", 0.10))

        # 2. IP literal as host
        if re.fullmatch(r"\d{1,3}(\.\d{1,3}){3}", host):
            score += 0.30
            signals.append(Signal("url.ip_host", "URL uses a raw IP address instead of a domain", 0.30))

        # 3. Punycode / homograph — a top impersonation vector (look-alike of a
        # real brand), so weighted strongly even on its own.
        if "xn--" in host:
            score += 0.45
            signals.append(Signal("url.punycode", "Internationalized (punycode) domain — homograph risk", 0.45))

        # 4. Suspicious TLD
        tld = host.rsplit(".", 1)[-1] if "." in host else ""
        if tld in _SUSPICIOUS_TLDS:
            score += 0.22
            signals.append(Signal("url.tld", f"High-abuse top-level domain '.{tld}'", 0.22))

        # 5. Shortener
        if host in _SHORTENERS:
            score += 0.22
            signals.append(Signal("url.shortener", "Shortened link hides the real destination", 0.22))

        # 6. Excessive subdomains
        labels = host.split(".")
        if len(labels) >= 4:
            score += 0.12
            signals.append(Signal("url.subdomains", "Unusually many subdomains", 0.12))

        # 7. Phishing keywords in host/path
        full = (host + parsed.path).lower()
        kw_hits = [k for k in _PHISH_KEYWORDS if k in full]
        if kw_hits:
            w = min(0.20, 0.05 * len(kw_hits))
            score += w
            signals.append(Signal("url.keywords", f"Phishing keywords in URL: {', '.join(kw_hits[:4])}", w))

        # 8. Brand token on non-official-looking domain
        brand_hits = [b for b in _BRAND_TOKENS if b in full]
        if brand_hits:
            score += 0.15
            signals.append(Signal("url.brand_in_path", f"Brand name '{brand_hits[0]}' embedded in untrusted URL", 0.15))

        # 9. High entropy host (random-looking / DGA)
        ent = _shannon_entropy(host.replace(".", ""))
        if ent > 3.6:
            score += 0.12
            signals.append(Signal("url.entropy", f"Random-looking domain (entropy={ent:.2f})", 0.12))

        # 10. Hyphen / digit heavy host
        if host.count("-") >= 3 or sum(c.isdigit() for c in host) >= 5:
            score += 0.08
            signals.append(Signal("url.noise", "Domain has many hyphens/digits", 0.08))

        score = min(1.0, score)
        confidence = 0.7 if signals else 0.5
        return DetectorResult(
            detector=self.name,
            score=score,
            confidence=confidence,
            signals=signals,
            explanation=f"URL risk features evaluated for host '{host}'.",
            extra={"host": host, "entropy": round(ent, 3), "tld": tld},
        )
