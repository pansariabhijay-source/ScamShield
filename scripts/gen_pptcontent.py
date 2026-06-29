#!/usr/bin/env python3
"""Generate pptcontent.pdf — slide-by-slide content for the India.runs Track 3
(Everyday AI) ideathon deck. Answers every template question, positions
ScamShield as the Trust & Safety layer of the Redrob ecosystem, and tells the
team which visual to drop on each slide.
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parent.parent
SHOTS = ROOT / "docs" / "shots"
HLD = ROOT / "docs" / "architecture" / "hld.png"

# palette
PURPLE = colors.HexColor("#6d28d9")
PURPLE_SOFT = colors.HexColor("#f3effe")
INK = colors.HexColor("#0f172a")
GREY = colors.HexColor("#64748b")
GREEN = colors.HexColor("#15803d")
GREEN_SOFT = colors.HexColor("#eafaf0")
AMBER_SOFT = colors.HexColor("#fff7 e6".replace(" ", ""))
LINE = colors.HexColor("#e3e7ee")

ss = getSampleStyleSheet()

# House style: never use the long em dash in copy (team preference).
_BaseParagraph = Paragraph


def Paragraph(textval, *args, **kwargs):  # noqa: F811 (intentional wrapper)
    if isinstance(textval, str):
        textval = textval.replace(" — ", ", ").replace("—", ", ")
    return _BaseParagraph(textval, *args, **kwargs)


def style(name, **kw):
    base = dict(fontName="Helvetica", fontSize=10.5, leading=15, textColor=INK, alignment=TA_LEFT)
    base.update(kw)
    return ParagraphStyle(name, **base)


S_TITLE = style("t", fontName="Helvetica-Bold", fontSize=15, leading=19, textColor=colors.white)
S_KICKER = style("k", fontName="Helvetica-Bold", fontSize=9, leading=12, textColor=colors.white)
S_H = style("h", fontName="Helvetica-Bold", fontSize=10.5, leading=14, textColor=PURPLE)
S_Q = style("q", fontSize=9.5, leading=13.5, textColor=GREY, fontName="Helvetica-Oblique")
S_B = style("b", fontSize=10, leading=15)
S_BOLD = style("bb", fontName="Helvetica-Bold", fontSize=10, leading=15)
S_TALK = style("talk", fontSize=9.5, leading=13.5, textColor=colors.HexColor("#14532d"))
S_VIS = style("vis", fontSize=9.5, leading=13.5, textColor=colors.HexColor("#7c2d12"))
S_SMALL = style("sm", fontSize=8.5, leading=12, textColor=GREY)


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def bullets(items):
    rows = []
    for it in items:
        rows.append(Paragraph(f"<font color='#6d28d9'>•</font>&nbsp;&nbsp;{it}", S_B))
        rows.append(Spacer(1, 3))
    return rows


def header_band(n, title):
    t = Table(
        [[Paragraph(f"SLIDE {n}", S_KICKER), Paragraph(esc(title), S_TITLE)]],
        colWidths=[24 * mm, None],
    )
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PURPLE),
        ("BACKGROUND", (0, 0), (0, 0), colors.HexColor("#4c1d95")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("ROUNDEDCORNERS", [6, 6, 6, 6]),
    ]))
    return t


def callout(label, body_paras, bg, border, label_style):
    inner = [Paragraph(label, label_style)] + body_paras
    t = Table([[inner]], colWidths=[None])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("BOX", (0, 0), (-1, -1), 0.8, border),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("ROUNDEDCORNERS", [8, 8, 8, 8]),
    ]))
    return t


def img(path: Path, width_mm):
    if not path.exists():
        return Paragraph(f"[missing image: {path.name}]", S_SMALL)
    w, h = PILImage.open(path).size
    width = width_mm * mm
    return Image(str(path), width=width, height=width * h / w)


story = []


# ---- cover ----------------------------------------------------------------
story.append(Spacer(1, 8 * mm))
story.append(Paragraph("ScamShield AI", style("c1", fontName="Helvetica-Bold", fontSize=30, leading=34, textColor=INK)))
story.append(Paragraph("Pitch-deck content &amp; talk track — slide by slide", style("c2", fontSize=13, leading=17, textColor=PURPLE, fontName="Helvetica-Bold")))
story.append(Spacer(1, 3 * mm))
story.append(Paragraph("India.runs · Track 3 — Everyday AI Innovation Challenge (Redrob × Hack2Skill)", S_SMALL))
story.append(Spacer(1, 6 * mm))
story.append(callout(
    "THE ONE-LINER (memorize this)",
    [Paragraph("<b>ScamShield is the AI trust layer that tells anyone — before they click, pay, or reply — whether something is safe or a scam, in plain language. Built into Redrob, it makes every job, message, recruiter and payment in the ecosystem verified-by-default.</b>", S_B)],
    PURPLE_SOFT, PURPLE, S_H,
))
story.append(Spacer(1, 5 * mm))
story.append(callout(
    "WINNING STRATEGY — why this scores on Track 3",
    bullets([
        "Slides 2–3 of the template say it outright: the score is about <b>fit with the Redrob ecosystem</b>. So we frame ScamShield not as a standalone app, but as the <b>Trust &amp; Safety layer of Redrob</b>.",
        "Redrob spans hiring, communication, workflows — exactly where everyday scams strike (fake recruiters, fake offers, ‘pay-to-get-hired’, phishing links, fraudulent UPI). ScamShield neutralizes them <b>inside</b> the ecosystem.",
        "New AI-native workflow introduced: <b>‘verify before you trust.’</b> Network effect: every scam reported anywhere immunizes every Redrob user — trust becomes the moat.",
        "Lead with the human story (protecting parents &amp; job-seekers); use the architecture &amp; live UI as proof you can actually build it.",
    ]),
    GREEN_SOFT, colors.HexColor("#86efac"), style("g", fontName="Helvetica-Bold", fontSize=9, leading=12, textColor=GREEN),
))
story.append(Spacer(1, 5 * mm))
story.append(callout(
    "INTERNAL BUILD NOTES — do NOT put on slides",
    bullets([
        "This is an <b>ideathon</b> (PDF only, no code submission, up to 5 appendix slides). You don’t need a finished product — you need a brilliantly-argued idea + proof you can build it. The working UI &amp; architecture you already have are a huge advantage; show them.",
        "Position <b>Redrob AI</b> as the reasoning/explanation engine. If you take this forward, actually wire Redrob’s AI so the claim stays true in Q&amp;A.",
        "All market figures below are from public I4C / RBI / NPCI reporting — <b>confirm the latest numbers</b> before submitting so you’re bulletproof if questioned.",
    ]),
    colors.HexColor("#fff7e6"), colors.HexColor("#fcd34d"), style("a", fontName="Helvetica-Bold", fontSize=9, leading=12, textColor=colors.HexColor("#92400e")),
))
story.append(PageBreak())


# ---- slide data -----------------------------------------------------------
def slide(n, title, questions, put, talk=None, visual=None, image=None, image_w=120, extra=None):
    global story
    story.append(header_band(n, title))
    story.append(Spacer(1, 4 * mm))
    if questions:
        story.append(callout(
            "QUESTIONS ON THIS SLIDE",
            [Paragraph("&nbsp;&nbsp;•&nbsp; " + esc(q), S_Q) for q in questions],
            colors.HexColor("#f8fafc"), LINE, style("ql", fontName="Helvetica-Bold", fontSize=8.5, leading=12, textColor=GREY),
        ))
        story.append(Spacer(1, 4 * mm))
    story.append(Paragraph("PUT THIS ON THE SLIDE", S_H))
    story.append(Spacer(1, 2 * mm))
    story += bullets(put)
    if extra:
        story.append(Spacer(1, 2 * mm))
        story += extra
    if talk:
        story.append(Spacer(1, 3 * mm))
        story.append(callout("SAY THIS (talk track)", [Paragraph(talk, S_TALK)], GREEN_SOFT, colors.HexColor("#86efac"),
                             style("tl", fontName="Helvetica-Bold", fontSize=8.5, leading=12, textColor=GREEN)))
    if visual:
        story.append(Spacer(1, 3 * mm))
        story.append(callout("VISUAL TO ADD", [Paragraph(visual, S_VIS)], colors.HexColor("#fff7e6"),
                             colors.HexColor("#fcd34d"), style("vl", fontName="Helvetica-Bold", fontSize=8.5, leading=12, textColor=colors.HexColor("#92400e"))))
    if image:
        story.append(Spacer(1, 3 * mm))
        story.append(img(image, image_w))
        story.append(Paragraph("↑ suggested visual (already captured for you in /docs)", S_SMALL))
    story.append(PageBreak())


slide(
    4, "Cover / Title slide",
    [],
    [
        "<b>Team Name:</b> [your team name]",
        "<b>Team Members:</b> [name — role], [name — role], …",
        "<b>Problem Statement:</b> Everyday Indians and users of AI-native platforms have no instant, trustworthy way to know if a message, job offer, link, or payment is genuine or a scam. <b>ScamShield is the AI trust layer that answers ‘Can I trust this?’ in seconds — and makes the Redrob ecosystem safe by default.</b>",
        "<b>Track:</b> Track 3 — Everyday AI Innovation Challenge.",
        "<b>Tagline under the logo:</b> “Before you click, pay, or trust — ScamShield tells you whether you should.”",
    ],
    visual="ScamShield logo + the product hero screenshot (docs/shots/hero.png). Keep it clean and confident.",
    image=SHOTS / "hero.png", image_w=150,
)

slide(
    5, "Problem We Want To Solve",
    ["What everyday challenge are you addressing?", "Who faces this challenge?", "Why does it matter?"],
    [
        "<b>The everyday challenge:</b> digital scams are now a daily tax on Indian life — fake job offers, KYC/bank frauds, fake delivery links, UPI ‘collect’ traps, and impersonation. Anyone with a phone is a target, every single day.",
        "<b>The scale (India):</b> Indians reported <b>₹11,333 crore</b> lost to cyber fraud in just the first 9 months of 2024 (I4C). Over <b>1.2 million</b> cybercrime complaints a year. With <b>13–14 billion UPI transactions / month</b>, the attack surface is the entire country.",
        "<b>Who faces it:</b> everyone — but hardest hit are first-time internet users, students chasing jobs, daily-wage earners, and especially <b>elderly parents</b> who can’t tell a fake bank SMS from a real one. On hiring/AI platforms specifically: job-seekers hit by fake recruiters and ‘pay-to-get-hired’ scams.",
        "<b>Why it matters:</b> one wrong tap = life savings gone, identity stolen, or a ‘job’ that costs money instead of paying it. The fear and shame break people’s trust in digital India. As more of life runs on AI and UPI, <b>unverified trust is the single biggest blocker to safe adoption.</b>",
    ],
    talk="“India is running faster on digital than anywhere on earth — but the faster we run, the more we’re scammed. ₹11,000 crore lost in nine months. And the people who can least afford it — our parents, students, first-time users — are the easiest targets.”",
    visual="A bold stat panel (₹11,333 cr · 1.2M+ complaints · 14B UPI txns/mo). Optionally the live scam-activity screenshot as a backdrop.",
)

slide(
    6, "Idea Overview",
    ["What is your AI-powered idea?", "How does it solve the problem?", "How could it fit within or enhance the Redrob ecosystem?"],
    [
        "<b>What it is:</b> ScamShield is an AI <b>trust layer</b>. Paste a message, upload a screenshot, drop a link, or scan a UPI/QR — and get an instant verdict: a <b>0–100 trust score</b>, the <b>exact reasons</b>, the <b>scam type</b>, and the <b>one action to take</b> — all in plain language anyone understands.",
        "<b>How it solves it:</b> it moves people from “I’m not sure, let me risk it” to “ScamShield already checked — 96% KYC scam, delete it.” Multiple AI detectors (language, links, impersonation, UPI patterns) fuse into one calibrated verdict, and an AI explainer turns it into human advice — in under 2 seconds.",
        "<b>How it fits / supercharges Redrob:</b> ScamShield becomes the <b>Trust &amp; Safety layer of the Redrob AI ecosystem</b>. Redrob spans hiring, communication and workflows — exactly where scams strike. Embedded in Redrob, every recruiter, job post, link and payment is <b>auto-verified</b>.",
        "<b>New value layer introduced:</b> a reusable ‘verify-before-you-trust’ workflow + a shared scam-intelligence graph. <b>Network effect:</b> every report anywhere makes every Redrob user safer. <b>“Verified by Redrob”</b> becomes a trust standard rivals can’t copy.",
    ],
    talk="“We’re not building another app. We’re building the trust layer Redrob is missing — so every interaction in the ecosystem is safe by default.”",
    visual="Left: the verdict screenshot (docs/shots/verdict.png). Right: a simple ‘ScamShield = Trust layer inside Redrob’ diagram.",
    image=SHOTS / "verdict.png", image_w=120,
)

slide(
    7, "Understanding The User",
    ["Who benefits from the solution?", "What challenges do they face?", "How does your idea improve their experience?"],
    [
        "<b>Who benefits:</b> (1) Everyday Indians &amp; their families — especially elderly parents. (2) Job-seekers targeted by fake recruiters &amp; fee scams. (3) Every Redrob user who messages, hires, or transacts inside the ecosystem.",
        "<b>Challenges today:</b> they can’t tell real from fake; scams weaponize urgency &amp; fear; advice is scattered and technical; by the time they Google it, the money’s already gone; elders feel isolated and ashamed to ask for help.",
        "<b>How ScamShield improves it:</b> one tap → a clear yes/no + why + what to do. <b>Family Mode</b> lets children protect parents remotely (forward → auto-check → gentle alert). Inside Redrob, trust signals appear <b>inline</b>, so users act with confidence instead of fear.",
    ],
    talk="“The people most targeted are the least equipped to defend themselves. ScamShield meets them exactly where they are — and lets a daughter protect her father from 1,000 km away.”",
    visual="3 persona cards (Parent · Job-seeker · Redrob user) + the Family Protection screenshot from the site.",
)

slide(
    8, "User Journey & Experience",
    ["How would someone use your solution?", "What does the experience look like?", "Why is it intuitive and easy to use?"],
    [
        "<b>Step 1 — Trigger:</b> Priya’s mother gets “Your SBI KYC expires today, click here.” She’s worried.",
        "<b>Step 2 — One action:</b> she forwards it to ScamShield (or pastes / scans it). No app expertise needed.",
        "<b>Step 3 — Instant verdict (&lt;2s):</b> “96% Scam — KYC fraud. Banks never ask this on WhatsApp. Delete &amp; block.”",
        "<b>Step 4 — Confident action:</b> she deletes it. Priya gets a calm alert that mom was targeted and protected.",
        "<b>Step 5 — Everyone safer:</b> that scam signature now shields every other user (community shield).",
        "<b>Why it’s intuitive:</b> one input, one answer, plain language, zero jargon; works on the channels people already use (WhatsApp / SMS / UPI); no setup, no sign-up to try.",
    ],
    talk="“The whole experience is one question and one answer. If my mother can use it without calling me, we’ve won.”",
    visual="RECOMMENDED BY TEMPLATE: a 5-panel User-Journey / Storyboard (the 5 steps above) + hero & verdict screenshots beneath it.",
    image=SHOTS / "hero.png", image_w=150,
)

slide(
    9, "AI-Powered Experience",
    ["Where does AI contribute value?", "What is automated, personalized, or improved?", "Why is AI important to the experience?"],
    [
        "<b>Where AI adds value:</b> (1) <b>Detection</b> — an AI ensemble reads intent, urgency, impersonation, link &amp; UPI risk. (2) <b>Explanation</b> — <b>Redrob AI</b> turns a raw risk score into a calm, human explanation + the right action. (3) <b>Personalization</b> — tuned to Indian scam patterns &amp; languages, learns each family’s risk profile. (4) <b>Automation</b> — auto-checks links/recruiters/payments inside Redrob with zero user effort.",
        "<b>What’s automated / personalized / improved:</b> the entire ‘is this safe?’ judgment is automated; advice is personalized to the user’s context and language; accuracy improves continuously from every report (active learning).",
        "<b>Why AI is essential:</b> scams mutate daily — rules alone can’t keep up. Only AI can read novel, localized, emotionally-manipulative messages and explain them in human terms at scale. <b>Powered by Redrob AI</b>, this reasoning layer is what turns raw signals into trust people actually understand and act on.",
    ],
    talk="“Rules block yesterday’s scam. AI understands tomorrow’s — and, powered by Redrob, explains it in words my grandmother gets.”",
    visual="The architecture (HLD) diagram + the ‘Aether’ AI demo screenshot to convey intelligence. Both are in /docs.",
    image=HLD, image_w=160,
)

slide(
    10, "Accessibility & Inclusivity",
    ["How can diverse users benefit?", "How does the solution remain accessible and easy to adopt?"],
    [
        "<b>Built for the next billion:</b> multilingual (Hindi + regional languages), low digital-literacy friendly (no jargon, read-aloud verdicts), elder-first (Family Mode + voice), and accessible by design (WCAG-AA contrast, screen-reader friendly, color is <b>never</b> the only signal, reduced-motion support).",
        "<b>Zero-friction adoption:</b> works where people already are — forward a WhatsApp message, paste an SMS, scan a QR. No new app to learn, no sign-up to try, one-tap actions, light enough for low-end devices.",
        "<b>Inclusion is the point:</b> the people most targeted are the least equipped to defend themselves — so accessibility isn’t a feature, it’s the mission.",
    ],
    talk="“If it only works for tech-savvy English speakers, it fails the people who need it most. So we built it for everyone — in their language, at their comfort level.”",
    visual="The mobile screenshot (docs/shots/mobile.png) + accessibility badges (AA contrast · screen-reader · reduced-motion · multilingual).",
    image=SHOTS / "mobile.png", image_w=58,
)

slide(
    11, "Impact & Real-World Benefits",
    ["What positive change could this create?", "How would users benefit?", "How could Redrob users or communities benefit from it?"],
    [
        "<b>Positive change:</b> flips India’s scam epidemic from ‘react after losing money’ to ‘prevented before the tap.’ Restores people’s confidence to transact, apply for jobs, and pay digitally.",
        "<b>How users benefit:</b> money saved, identity protected, anxiety replaced with a clear answer; elders protected without losing dignity; job-seekers dodge fee scams &amp; fake offers.",
        "<b>How Redrob &amp; its communities benefit:</b> the ecosystem becomes <b>safe by default</b> — fewer fraud losses, and trust → higher engagement &amp; retention (trust is the ultimate network-effect moat). Every report grows a shared scam-intelligence graph that protects the whole community. <b>‘Verified by Redrob’</b> becomes a competitive advantage no standalone app can match.",
        "<b>Projected impact:</b> even a 10% cut in cyber-fraud losses keeps <b>₹1,000+ crore a year</b> in everyday Indians’ pockets.",
    ],
    talk="“Trust is the highest-leverage feature any ecosystem can have. Make Redrob the safest place to act online, and engagement, retention and reputation all compound.”",
    visual="Impact stat panel + the live scam-map / recent-activity screenshot to show real-time community protection.",
)

slide(
    12, "Future Potential",
    ["How could the solution evolve?", "What additional features or use cases could emerge?"],
    [
        "<b>From checker → always-on guardian:</b> real-time interception (browser, keyboard, call-screening), privacy-first on-device models, and deeper Redrob-native trust scores on every recruiter, post and payment.",
        "<b>New features &amp; use cases:</b> voice / call-scam detection (digital-arrest scams), WhatsApp &amp; Telegram bot, browser extension, merchant/UPI verification API, deepfake &amp; voice-clone detection, enterprise trust dashboard.",
        "<b>Ecosystem play:</b> ScamShield becomes Redrob’s <b>trust infrastructure</b> — a ‘Verified by Redrob’ standard licensed across India’s digital economy (banks, marketplaces, gig &amp; hiring platforms).",
        "<b>The vision:</b> the default trust layer the next billion Indians run on — literally ‘what India runs on.’",
    ],
    talk="“We start by protecting one forwarded message. We end as the trust layer India’s digital economy runs on — and Redrob owns that standard.”",
    visual="A 3-stage roadmap timeline: NOW (trust analyzer) → NEXT (real-time + bot + API) → VISION (Verified-by-Redrob standard).",
)

# ---- appendix divider ------------------------------------------------------
story.append(header_band("A", "Optional Appendix — 5 ready-to-paste slides (PDF, no code required)"))
story.append(Spacer(1, 3 * mm))
story.append(Paragraph(
    "The template allows up to 5 appendix slides. Below are 5 built for you, each on its own page. "
    "Paste one per appendix slide. They add credibility (you can build it) and ambition (size of the prize).",
    S_B))
story.append(PageBreak())

# mark styles for the comparison matrix
S_YES = style("yes", fontName="Helvetica-Bold", fontSize=9, leading=11, textColor=colors.HexColor("#16a34a"), alignment=1)
S_NO = style("no", fontSize=9, leading=11, textColor=colors.HexColor("#94a3b8"), alignment=1)
S_MID = style("mid", fontName="Helvetica-Bold", fontSize=9, leading=11, textColor=colors.HexColor("#d97706"), alignment=1)
S_CELL = style("cell", fontSize=8.2, leading=10.5)
S_CHEAD = style("chead", fontName="Helvetica-Bold", fontSize=8.2, leading=10.5, textColor=colors.white, alignment=1)


def _m(kind):
    return Paragraph({"y": "✓", "n": "✕", "~": "~"}[kind], {"y": S_YES, "n": S_NO, "~": S_MID}[kind])


def comp_table():
    head = ["Capability", "ScamShield", "Truecaller", "Bank SMS\nfilter", "Manual\nGoogling", "Generic AI\nchatbot"]
    rows = [
        ("Plain-language ‘why it’s a scam’ + what to do", "y", "n", "n", "~", "~"),
        ("Multi-channel: SMS · WhatsApp · URL · UPI · QR · screenshot", "y", "~", "n", "~", "n"),
        ("Family / elder protection (forward &amp; alert)", "y", "n", "n", "n", "n"),
        ("Tuned to Indian scams (KYC · UPI · courier · job)", "y", "~", "~", "n", "n"),
        ("Real-time, proactive verdict (&lt;2s)", "y", "~", "~", "n", "n"),
        ("Ecosystem-native: verify recruiters / payments inline", "y", "n", "n", "n", "n"),
        ("Community scam-intelligence (network effect)", "y", "~", "n", "n", "n"),
    ]
    data = [[Paragraph(h.replace("\n", "<br/>"), S_CHEAD) for h in head]]
    for cap, *marks in rows:
        data.append([Paragraph(cap, S_CELL)] + [_m(k) for k in marks])
    t = Table(data, colWidths=[58 * mm, 26 * mm, 23 * mm, 23 * mm, 23 * mm, 25 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PURPLE),
        ("BACKGROUND", (1, 1), (1, -1), PURPLE_SOFT),  # highlight ScamShield column
        ("ROWBACKGROUNDS", (0, 1), (0, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ("GRID", (0, 0), (-1, -1), 0.5, LINE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return t


def tam_table():
    rows = [
        ("TAM", "Every Indian smartphone user — anyone who messages or pays online", "≈ 750M+ users"),
        ("SAM", "Digitally-active Indians exposed to scams (UPI / messaging / hiring)", "≈ 400M+ users"),
        ("SOM (entry)", "Redrob’s users + India hiring / gig platforms, year 1", "Land via Redrob"),
    ]
    data = [[Paragraph("Layer", S_CHEAD), Paragraph("Who", S_CHEAD), Paragraph("Size", S_CHEAD)]]
    for a, b, c in rows:
        data.append([Paragraph(f"<b>{a}</b>", S_CELL), Paragraph(b, S_CELL), Paragraph(f"<b>{c}</b>", S_CELL)])
    t = Table(data, colWidths=[30 * mm, 110 * mm, 38 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PURPLE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ("GRID", (0, 0), (-1, -1), 0.5, LINE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7), ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


def caption(text):
    return Paragraph(text, S_SMALL)


slide(
    "A1", "Appendix · System Architecture (HLD)", [],
    [
        "Thin FastAPI routes + dependency injection → services → a multi-engine <b>detector ensemble</b> → calibrated verdict.",
        "Heavy OCR / LLM work is offloaded to <b>Celery</b> so the user still gets a verdict in under 2 seconds.",
        "PostgreSQL (scans, predictions, risk factors) + Redis (cache &amp; broker). Built to plug Redrob AI in as the reasoning engine.",
    ],
    visual="Use the diagram below full-width. It signals ‘this is real and buildable,’ which judges reward.",
    image=HLD, image_w=170,
)

slide(
    "A2", "Appendix · Product (already designed &amp; working)", [],
    [
        "Not a concept — a working, premium UI. Show the hero, the live verdict, and the mobile view.",
        "The 96% verdict screen (score ring + reasons + plain-language explanation + one-tap actions) is your single most persuasive image.",
    ],
    extra=[
        img(SHOTS / "hero.png", 150), caption("↑ Landing + trust analyzer"), Spacer(1, 3 * mm),
        img(SHOTS / "verdict.png", 120), caption("↑ Live verdict: 96% scam, reasons, explain-like-a-human, actions"),
    ],
)

slide(
    "A3", "Appendix · User Flow (process flow)", [],
    [
        "<b>Receive</b> a suspicious message → <b>Forward / paste / scan</b> to ScamShield → <b>AI ensemble analyzes</b> "
        "(language · links · impersonation · UPI) → <b>Verdict in &lt;2s</b> (score + reasons + action) → "
        "<b>User acts safely</b> → <b>Community shielded</b> (signature shared).",
        "Family path: parent forwards → auto-checked → child gets a calm alert that mom was targeted and protected.",
        "Redrob path: every recruiter message / job post / payment is auto-verified inline, no user effort.",
    ],
    visual="Draw this as a 6-box horizontal flow (Receive → Submit → Analyze → Verdict → Act → Community). Use the mobile shot beside it.",
    image=SHOTS / "mobile.png", image_w=56,
)

slide(
    "A4", "Appendix · Competitive Analysis", [],
    ["Why nothing else covers this: existing tools block calls or filter SMS, but none explain, cover every channel, protect families, or live natively inside an AI ecosystem."],
    extra=[Spacer(1, 1 * mm), comp_table(), Spacer(1, 2 * mm),
           caption("✓ = strong   ·   ~ = partial   ·   ✕ = none.  ScamShield is the only explainable, multi-channel, ecosystem-native option.")],
)

slide(
    "A5", "Appendix · Market Insights &amp; TAM", [],
    [
        "<b>The problem is enormous and growing:</b> ₹11,333 cr lost to cyber fraud in 9 months of 2024 (I4C); 1.2M+ complaints / year; 13–14B UPI transactions / month.",
        "<b>Why now:</b> UPI + AI-generated scams are exploding, government is pushing safety (1930 helpline, DoT), and <b>trust is the bottleneck</b> to the next phase of digital India.",
        "<b>Wedge → expansion:</b> land via Redrob’s ecosystem, expand to every Indian who messages and pays. Trust is a horizontal layer for the entire digital economy.",
    ],
    extra=[Spacer(1, 1 * mm), tam_table(), Spacer(1, 2 * mm),
           caption("Figures from public I4C / RBI / NPCI reporting — confirm the latest numbers before submission.")],
)

# ---- assets index ----------------------------------------------------------
story.append(callout(
    "ASSETS ALREADY CAPTURED FOR YOU (in the repo)",
    bullets([
        "docs/architecture/hld.png  —  high-level architecture diagram",
        "docs/shots/hero.png  —  landing + trust analyzer",
        "docs/shots/verdict.png  —  96% scam verdict (score ring, reasons, action)",
        "docs/shots/aether.png  —  AI ‘intelligence’ visual",
        "docs/shots/mobile.png  —  mobile / accessibility view",
    ]),
    PURPLE_SOFT, PURPLE, S_H,
))

# ---- build ----------------------------------------------------------------
doc = SimpleDocTemplate(
    str(ROOT / "pptcontent.pdf"),
    pagesize=A4,
    leftMargin=16 * mm, rightMargin=16 * mm, topMargin=14 * mm, bottomMargin=14 * mm,
    title="ScamShield AI — Track 3 deck content", author="ScamShield AI",
)
doc.build(story)
print("wrote", ROOT / "pptcontent.pdf")
