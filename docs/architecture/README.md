# Architecture — High-Level Design

![ScamShield AI — High-Level Design](./hld.png)

- **`hld.svg`** — source vector (crisp at any zoom).
- **`hld.png`** — rasterized export (4778×3278) for docs, slides, README embeds.

## What it shows

Request flow top → bottom:

1. **Clients** — web app, family-forwarded messages, screenshot/QR capture.
2. **Frontend (Next.js 15 / React 19)** — App Router pages, shadcn-style design
   system, Zustand state, React Query cache, the trust analyzer UI.
3. **Backend API (FastAPI)** — thin routers (`auth · detect · history · stats ·
   admin · health`), middleware, dependency injection, Pydantic schemas. The
   frontend reaches it via the Next.js `/api/v1/*` rewrite proxy.
4. **Application services** — orchestration / unit-of-work per request.
5. **Detection domain & persistence** — detector ensemble (text/URL/UPI
   heuristics, OCR, LLM explainer) + repositories.
6. **Data, async & external** — PostgreSQL, Redis (cache + Celery broker),
   Celery workers for heavy OCR/LLM, object storage, and the Redrob LLM.
7. **Cross-cutting** — observability, security, config, delivery.

Dashed boxes are third-party/external services.

## Regenerate

```bash
python scripts/gen_hld.py     # writes docs/architecture/hld.svg
node   scripts/svg_to_png.js  # writes docs/architecture/hld.png
```
