#!/usr/bin/env python3
"""ScamShield AI — High-Level Design as an icon-based request-flow diagram.

Boxes-and-arrows style (laptop / servers / DB / cache icons + labeled edges),
pure stdlib string templating. Run:  python scripts/gen_hld.py
"""
from __future__ import annotations

import html
import math
from pathlib import Path

W, H = 1340, 880
INK = "#0f172a"
SUB = "#64748b"
parts: list[str] = []


def esc(s):
    return html.escape(str(s), quote=True)


def text(x, y, s, size=13, color=INK, weight="400", anchor="start", spacing="0"):
    return (
        f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{weight}" '
        f'text-anchor="{anchor}" letter-spacing="{spacing}" '
        f'font-family="Inter, \'SF Pro Display\', system-ui, sans-serif">{esc(s)}</text>'
    )


# ----------------------------------------------------------------- icons
def ic_laptop(cx, cy, c):
    return (
        f'<rect x="{cx-28}" y="{cy-26}" width="56" height="40" rx="6" fill="#fff" stroke="{c}" stroke-width="3"/>'
        f'<rect x="{cx-21}" y="{cy-20}" width="42" height="28" rx="3" fill="{c}" opacity="0.12"/>'
        f'<path d="M{cx-37} {cy+16} L{cx+37} {cy+16} L{cx+31} {cy+25} L{cx-31} {cy+25} Z" '
        f'fill="#fff" stroke="{c}" stroke-width="3" stroke-linejoin="round"/>'
    )


def ic_server(cx, cy, c):
    g = [
        f'<rect x="{cx-26}" y="{cy-26}" width="52" height="24" rx="6" fill="#fff" stroke="{c}" stroke-width="3"/>',
        f'<rect x="{cx-26}" y="{cy+2}" width="52" height="24" rx="6" fill="#fff" stroke="{c}" stroke-width="3"/>',
        f'<circle cx="{cx-15}" cy="{cy-14}" r="3" fill="{c}"/>',
        f'<circle cx="{cx-15}" cy="{cy+14}" r="3" fill="{c}"/>',
        f'<line x1="{cx-4}" y1="{cy-14}" x2="{cx+16}" y2="{cy-14}" stroke="{c}" stroke-width="2.5" stroke-linecap="round"/>',
        f'<line x1="{cx-4}" y1="{cy+14}" x2="{cx+16}" y2="{cy+14}" stroke="{c}" stroke-width="2.5" stroke-linecap="round"/>',
    ]
    return "".join(g)


def ic_chip(cx, cy, c):
    g = [f'<rect x="{cx-22}" y="{cy-22}" width="44" height="44" rx="9" fill="#fff" stroke="{c}" stroke-width="3"/>',
         f'<rect x="{cx-10}" y="{cy-10}" width="20" height="20" rx="4" fill="{c}" opacity="0.16" stroke="{c}" stroke-width="2"/>']
    for k in range(3):
        off = -8 + k * 8
        g.append(f'<line x1="{cx+off}" y1="{cy-30}" x2="{cx+off}" y2="{cy-22}" stroke="{c}" stroke-width="2.5" stroke-linecap="round"/>')
        g.append(f'<line x1="{cx+off}" y1="{cy+22}" x2="{cx+off}" y2="{cy+30}" stroke="{c}" stroke-width="2.5" stroke-linecap="round"/>')
        g.append(f'<line x1="{cx-30}" y1="{cy+off}" x2="{cx-22}" y2="{cy+off}" stroke="{c}" stroke-width="2.5" stroke-linecap="round"/>')
        g.append(f'<line x1="{cx+22}" y1="{cy+off}" x2="{cx+30}" y2="{cy+off}" stroke="{c}" stroke-width="2.5" stroke-linecap="round"/>')
    return "".join(g)


def ic_cache(cx, cy, c):
    g = []
    for i, off in enumerate((-20, -2, 16)):
        g.append(f'<rect x="{cx-26}" y="{cy+off}" width="52" height="15" rx="5" fill="#fff" stroke="{c}" stroke-width="2.6"/>')
        g.append(f'<circle cx="{cx-17}" cy="{cy+off+7}" r="2.4" fill="{c}"/>')
    return "".join(g)


def ic_db(cx, cy, c):
    return (
        f'<path d="M{cx-26} {cy-20} L{cx-26} {cy+18} A26 9 0 0 0 {cx+26} {cy+18} L{cx+26} {cy-20}" '
        f'fill="#fff" stroke="{c}" stroke-width="3" stroke-linejoin="round"/>'
        f'<ellipse cx="{cx}" cy="{cy-20}" rx="26" ry="9" fill="{c}" opacity="0.14" stroke="{c}" stroke-width="3"/>'
        f'<path d="M{cx-26} {cy-2} A26 9 0 0 0 {cx+26} {cy-2}" fill="none" stroke="{c}" stroke-width="2" opacity="0.55"/>'
    )


def ic_gear(cx, cy, c):
    g = [f'<circle cx="{cx}" cy="{cy}" r="16" fill="#fff" stroke="{c}" stroke-width="3"/>',
         f'<circle cx="{cx}" cy="{cy}" r="6" fill="{c}" opacity="0.18" stroke="{c}" stroke-width="2"/>']
    for k in range(8):
        a = k * 45
        g.append(
            f'<g transform="rotate({a} {cx} {cy})"><rect x="{cx-3.5}" y="{cy-26}" width="7" height="9" rx="2" '
            f'fill="#fff" stroke="{c}" stroke-width="2.4"/></g>'
        )
    return "".join(g)


def ic_sparkle(cx, cy, c):
    def star(x, y, r, rr):
        return (
            f'<path d="M{x} {y-r} C{x+rr} {y-rr} {x+rr} {y-rr} {x+r} {y} '
            f'C{x+rr} {y+rr} {x+rr} {y+rr} {x} {y+r} '
            f'C{x-rr} {y+rr} {x-rr} {y+rr} {x-r} {y} '
            f'C{x-rr} {y-rr} {x-rr} {y-rr} {x} {y-r} Z" fill="{c}"/>'
        )
    return star(cx - 4, cy + 2, 22, 4) + star(cx + 17, cy - 16, 9, 1.5)


# ----------------------------------------------------------------- node
def node(cx, cy, icon, title, sub, c, external=False):
    if external:
        parts.append(
            f'<rect x="{cx-78}" y="{cy-46}" width="156" height="118" rx="16" fill="#faf7ff" '
            f'stroke="#c9b6f0" stroke-width="1.6" stroke-dasharray="6 5"/>'
        )
        parts.append(text(cx + 70, cy - 32, "external", size=10, color="#a78bda", weight="700", anchor="end"))
    parts.append(icon(cx, cy, c))
    parts.append(text(cx, cy + 48, title, size=14.5, color=INK, weight="700", anchor="middle"))
    parts.append(text(cx, cy + 65, sub, size=11.5, color=SUB, anchor="middle"))


# ----------------------------------------------------------------- edges
def _unit(x1, y1, x2, y2):
    d = math.hypot(x2 - x1, y2 - y1) or 1
    return (x2 - x1) / d, (y2 - y1) / d


def edge(n1, n2, label, color="#334155", dashed=False, badge=None, r1=46, r2=58, lift=0):
    x1, y1 = n1
    x2, y2 = n2
    ux, uy = _unit(x1, y1, x2, y2)
    sx, sy = x1 + ux * r1, y1 + uy * r1
    ex, ey = x2 - ux * r2, y2 - uy * r2
    marker = {"#334155": "ad", "#10b981": "ag", "#7c3aed": "ap", "#3b82f6": "ab"}[color]
    dash = ' stroke-dasharray="7 5"' if dashed else ""
    parts.append(
        f'<line x1="{sx}" y1="{sy}" x2="{ex}" y2="{ey}" stroke="{color}" stroke-width="2.4"{dash} '
        f'marker-end="url(#{marker})"/>'
    )
    mx, my = (sx + ex) / 2, (sy + ey) / 2 - lift
    w = len(label) * 6.6 + 18
    parts.append(f'<rect x="{mx-w/2}" y="{my-12}" width="{w}" height="22" rx="11" fill="#ffffff" stroke="#e3e7ee" stroke-width="1"/>')
    parts.append(text(mx, my + 3.5, label, size=11, color="#475569", weight="600", anchor="middle"))
    if badge is not None:
        parts.append(f'<circle cx="{sx+ux*16}" cy="{sy+uy*16}" r="10" fill="{color}"/>')
        parts.append(text(sx + ux * 16, sy + uy * 16 + 4, badge, size=11, color="#fff", weight="700", anchor="middle"))


# ================================================================= canvas
parts.append(f'<rect x="0" y="0" width="{W}" height="{H}" fill="#ffffff"/>')
parts.append(f'<rect x="20" y="20" width="{W-40}" height="{H-40}" rx="22" fill="#fbfcfe" stroke="#eef1f6" stroke-width="1.5"/>')
parts.append(text(52, 66, "ScamShield AI", size=26, color=INK, weight="800", spacing="-0.5"))
parts.append(text(52, 92, "High-Level Design — request flow from “Can I trust this?” to a verdict", size=13.5, color=SUB))
parts.append(text(W - 52, 66, "synchronous verdict < 2s", size=12.5, color="#7c3aed", weight="700", anchor="end"))
parts.append(text(W - 52, 88, "heavy OCR / LLM offloaded async", size=11.5, color=SUB, anchor="end"))

# node positions
CLIENT = (150, 430)
API = (440, 430)
REDIS = (720, 290)
DETECT = (730, 560)
PG = (1010, 470)
CELERY = (1010, 690)
CLAUDE = (1230, 690)

# colors
C_SLATE, C_INDIGO, C_RED, C_AMBER, C_BLUE, C_GREEN, C_PURPLE = (
    "#6366f1", "#4f46e5", "#ef4444", "#f59e0b", "#3b82f6", "#16a34a", "#7c3aed",
)

# edges (drawn before nodes so icons sit on top)
edge(CLIENT, API, "POST /api/v1/detect", badge="1")
edge(API, REDIS, "check cache", badge="2")
edge(REDIS, API, "cache hit → verdict", color="#10b981", dashed=True, r1=58, r2=46, lift=-26)
edge(API, DETECT, "cache miss → analyze", badge="3")
edge(DETECT, PG, "save scan + verdict", color="#3b82f6", badge="4")
edge(DETECT, CELERY, "heavy OCR / LLM (async)", color="#334155", dashed=True, badge="5")
edge(CELERY, CLAUDE, "explain", color="#7c3aed", dashed=True, r2=70)

# green return loop: API -> down -> left -> up into client
parts.append(
    f'<path d="M{API[0]} {API[1]+58} L{API[0]} {800} L{CLIENT[0]} {800} L{CLIENT[0]} {CLIENT[1]+60}" '
    f'fill="none" stroke="#10b981" stroke-width="2.4" stroke-dasharray="7 5" marker-end="url(#ag)"/>'
)
parts.append(f'<rect x="{(API[0]+CLIENT[0])/2-118}" y="788" width="236" height="22" rx="11" fill="#ffffff" stroke="#e3e7ee"/>')
parts.append(text((API[0] + CLIENT[0]) / 2, 803, "trust verdict — score · reasons · action", size=11, color="#0f9d63", weight="700", anchor="middle"))

# nodes
node(*CLIENT, ic_laptop, "Client", "web · paste / upload / QR", C_SLATE)
node(*API, ic_server, "FastAPI", "routers + services (DI)", C_INDIGO)
node(*REDIS, ic_cache, "Redis", "cache + Celery broker", C_RED)
node(*DETECT, ic_chip, "Detection ensemble", "text · URL · UPI · OCR", C_AMBER)
node(*PG, ic_db, "PostgreSQL", "scans · predictions", C_BLUE)
node(*CELERY, ic_gear, "Celery worker", "async OCR / LLM jobs", C_GREEN)
node(*CLAUDE, ic_sparkle, "Redrob LLM", "human explanation", C_PURPLE, external=True)

# legend
ly = H - 42
parts.append(f'<line x1="52" y1="{ly}" x2="86" y2="{ly}" stroke="#334155" stroke-width="2.4" marker-end="url(#ad)"/>')
parts.append(text(94, ly + 4, "sync call", size=11.5, color=SUB))
parts.append(f'<line x1="182" y1="{ly}" x2="216" y2="{ly}" stroke="#334155" stroke-width="2.4" stroke-dasharray="7 5" marker-end="url(#ad)"/>')
parts.append(text(224, ly + 4, "async / deferred", size=11.5, color=SUB))
parts.append(f'<line x1="356" y1="{ly}" x2="390" y2="{ly}" stroke="#10b981" stroke-width="2.4" stroke-dasharray="7 5" marker-end="url(#ag)"/>')
parts.append(text(398, ly + 4, "response path", size=11.5, color=SUB))

# ----------------------------------------------------------------- assemble
def marker(mid, color):
    return (
        f'<marker id="{mid}" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="7" markerHeight="7" '
        f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{color}"/></marker>'
    )


svg = (
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
    f'<defs>{marker("ad", "#334155")}{marker("ag", "#10b981")}{marker("ap", "#7c3aed")}{marker("ab", "#3b82f6")}</defs>'
    + "".join(parts)
    + "</svg>"
)

out = Path(__file__).resolve().parent.parent / "docs" / "architecture" / "hld.svg"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(svg, encoding="utf-8")
print(f"wrote {out} ({len(svg):,} bytes)")
