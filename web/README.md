# ScamShield AI — Frontend

> _“Before you click, pay, scan, or trust something online, ScamShield tells you whether you should.”_

A premium, light-theme web experience for an AI digital-trust platform. Built to feel like
Apple Intelligence × Linear × Stripe — **security for humans, not cybersecurity experts.**

```bash
npm install
npm run dev        # http://localhost:3000  (DEMO mode — no backend needed)
```

Demo mode ships curated verdicts so the product is fully interactive offline. Set
`NEXT_PUBLIC_LIVE_API=1` to call the real FastAPI `/api/v1/detect/text` endpoint
(proxied via `next.config.ts` rewrites — see `.env.example`).

---

## 1 · Design philosophy & visual direction

A **calm verdict machine.** Most security tools shout; ScamShield whispers with authority.

| Principle | In practice |
|---|---|
| **One question, one answer** | Hero asks *“Can I trust this?”*, gives one magical input, returns one verdict. |
| **Light, air, one accent** | White canvas, `#FAFAFA`/`#F5F7FA` cards, a single soft royal blue (`#3B6CF6`). |
| **Color = meaning** | Emerald/amber/red appear *only* on verdicts. When you see red, it matters. |
| **Glass as a lens** | Frosting only where “AI thinks” — input card, nav, score halo. Everywhere else: flat & quiet. |
| **Motion that explains** | The ring draws itself, reasons slide in like an expert listing evidence, the human summary lands last. |

---

## 2 · Page hierarchy

```
/ (Landing — single scroll narrative)
├─ Navbar              floating glass pill, anchor nav
├─ Hero                "Can I trust this?" + magical input + inline AnalysisPanel
│   └─ AnalysisPanel   ← appears in place after "Analyze trust"
│       ├─ TrustScoreRing      animated circular verdict
│       ├─ Reasoning chips     "Why ScamShield thinks this"
│       ├─ Explain like a human
│       ├─ Category card
│       ├─ Recommended actions (1-tap)
│       └─ Engine consensus bars
├─ HowItWorks          3-step explainer
├─ FamilyProtection    "Protect your parents online" + chat mockup
├─ ScamMap             live India activity map + trend + hotspots
├─ RecentScans         Linear-style timeline cards
├─ FinalCTA            gradient conversion panel
└─ Footer
```

## 3 · Component tree

```
app/layout.tsx → Providers (React Query) → app/page.tsx
  Navbar · Hero · HowItWorks · FamilyProtection · ScamMap · RecentScans · FinalCTA · Footer

shared:   Logo
ui:       Button (cva variants) · Card · Eyebrow · Badge
landing:  Navbar · Hero · TrustInput · AnimatedPlaceholder · SectionHeading
          HowItWorks · FamilyProtection · ScamMap · RecentScans · FinalCTA · Footer
analysis: AnalysisPanel (Thinking / Error / Result) · TrustScoreRing
state:    store/useAnalysis (Zustand)  ·  lib/api  ·  lib/mock  ·  lib/types  ·  lib/verdict
```

## 4 · Folder structure

```
web/
├─ app/            layout · page · providers · globals.css (design tokens)
├─ components/
│  ├─ ui/          button · card · badge       (shadcn-style primitives)
│  ├─ shared/      logo
│  ├─ landing/     nav, hero, sections, map, timeline, footer
│  └─ analysis/    AnalysisPanel · TrustScoreRing
├─ lib/            types (backend mirror) · verdict palette · api · mock · utils
├─ store/          useAnalysis (Zustand)
└─ public/
```

## 5 · Tailwind design tokens (`app/globals.css` → `@theme`)

- **Brand:** `trust-50…900` (royal blue, `500 = #3B6CF6`).
- **Verdict:** `safe` (emerald), `warn` (amber), `scam` (soft red `#F1646C`) — used only on results.
- **Surfaces:** `canvas #FFFFFF`, `offwhite #FAFAFA`, `card #F5F7FA`, `line #ECEEF3`.
- **Ink:** `ink`, `ink-soft`, `ink-faint` text ramp.
- **Radii:** `xl 16` · `2xl 20` · `3xl 24`.
- **Shadows:** `soft` · `card` · `float` (all low-opacity, no harsh edges).
- **Easing:** `--ease-out-soft: cubic-bezier(0.22,1,0.36,1)` everywhere.
- **Utilities:** `.glass`, `.glass-strong`, `.text-gradient`, `.aura`, `.grid-dots`, `.live-pulse`, `.caret`.

## 6 · Animation specifications

| Element | Motion | Timing |
|---|---|---|
| Hero headline/sub | fade + rise 18px, staggered | 0.6–0.7s, ease-out-soft |
| Input card | rise + scale 0.98→1; glow halo on hover/focus | 0.8s, delay 0.25s |
| Placeholder | typewriter type→hold→delete→cycle + blinking caret | 46/28ms/char |
| Mode tabs | shared-layout pill (`layoutId`) | spring 380/32 |
| Trust ring | `strokeDashoffset` sweep + integer count-up in lockstep | 1.5s, delay 0.15s |
| Reasons | slide/fade in, 0.13s stagger | 0.5s each |
| Actions | slide-in from left, 0.12s stagger | after ring |
| Human summary | fades in **last** (delay 1.05s) | 0.6s |
| Map nodes | spring pop-in + infinite `live-pulse` halo | staggered 0.08s |
| Section reveals | `whileInView` once, rise 22–26px | 0.6s |

All motion respects `prefers-reduced-motion` (globally neutralized in CSS).

## 7 · Key component props

```ts
Button   { variant?: "primary"|"secondary"|"ghost"|"subtle"; size?: "sm"|"md"|"lg" }
TrustScoreRing { score: number; tone: "safe"|"warn"|"scam"; label: string }
SectionHeading { eyebrow: string; title: ReactNode; subtitle?: string; align?: "center"|"left" }
AnimatedPlaceholder { active: boolean }
// AnalysisPanel & TrustInput read/write the Zustand store (no props).
```

`lib/types.ts` mirrors the backend `DetectionResult` / `ScanSummary` / enums exactly,
so swapping mock → live is a zero-shape change.

## 8 · Implementation status

✅ Design tokens · UI primitives · landing narrative · interactive analysis flow
(Zustand + React Query ready) · responsive + reduced-motion + a11y · `npm run build` passes.

**Next:** dedicated `/analysis/[id]` route, camera QR scanner, auth + real history, i18n (Hindi + regional).

## 9 · Mobile responsiveness strategy

- Mobile-first; `sm/md/lg` breakpoints. Result grid `1fr` → `lg:[1fr_1.25fr]`.
- Input mode tabs scroll horizontally (hidden scrollbar) on small screens.
- Touch targets ≥ 44px; secondary CTAs collapse, icons persist.
- Fluid type via `clamp()` for every display heading. Map nodes use `%` positioning.

## 10 · Accessibility strategy

- Semantic landmarks (`header`/`main`/`section`/`footer`), single `h1`, ordered headings.
- All controls keyboard-reachable; visible `focus-visible` ring (`trust-400`, 2px offset).
- `⌘/Ctrl + Enter` submits the analyzer; `aria-label`s on icon-only & input controls.
- Verdict never relies on color alone — always paired with a text label + icon.
- `prefers-reduced-motion` disables all animation. AA+ contrast on ink ramp over surfaces.
```
