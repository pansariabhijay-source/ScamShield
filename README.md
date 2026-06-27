# ScamShield AI — Backend

Production-grade backend for an AI-powered scam-detection platform. Submit a
message, email, URL, UPI payment, or screenshot and receive a calibrated scam
risk verdict with **explainable reasons** and a **recommended action**.

```json
{
  "scam_probability": 96,
  "risk_level": "SCAM",
  "category": "KYC Scam",
  "reasons": [
    "Requests sensitive credentials (OTP/PIN/CVV)",
    "KYC / account-verification lure",
    "Asks for sensitive credentials while posing as bank",
    "Shortened link hides the real destination"
  ],
  "recommendation": "Do not click links or share information. Block the sender and report to your bank / cybercrime portal (1930 in India)."
}
```

---

## Architecture

```
            ┌────────────────────────────────────────────┐
   client ──►  FastAPI (api/) — thin routes + DI          │
            │      │                                       │
            │      ▼                                       │
            │  Services (services/) — orchestration / UoW  │
            │      │                  │                     │
            │      ▼                  ▼                     │
            │  Repositories      Ensemble (detectors/)      │
            │  (repositories/)        │                     │
            │      │            ┌─────┴──────┐              │
            │      ▼            ▼            ▼              │
            │  PostgreSQL   Text/URL/UPI   OCR/LLM (→Celery)│
            └────────────────────────────────────────────┘
                         Redis (cache + Celery broker)
```

**Key design principles**

| Concern | Decision |
|---|---|
| Engine pluggability | Every detector implements `BaseDetector.analyze → DetectorResult`. New engine = 1 class + 1 line in `detectors/registry.py`. |
| Separation of concerns | `api → services → repositories → db`. Routes never touch SQLAlchemy. |
| Latency | Text/URL/UPI run in-request; OCR/LLM can be offloaded to Celery (`workers/`). |
| Model swap | Heuristic implementations sit behind the *same* interface as DistilBERT/XGBoost/PaddleOCR. Flip `ENABLE_HEAVY_MODELS=true` to load real models — zero API changes. |
| Explainability | Each engine emits weighted `Signal`s persisted as `RiskFactor` rows for auditing & active learning. |
| Observability | Structured JSON logs, Prometheus `/metrics`, OpenTelemetry tracing, request IDs, Sentry hook. |
| Scale to 10M users | Stateless API (scale horizontally), bounded pools behind PgBouncer, Redis cache, async heavy work, partition-ready indexed schema. |

### The 7 detection engines (`app/detectors/`)
1. **TextDetector** — NLP scam classifier (urgency, threats, KYC, lottery, investment, job, credential-theft).
2. **URLDetector** — TLD/entropy/shortener/punycode/phishing-keyword reputation.
3. **OCRDetector** — extracts text from screenshots (EasyOCR/PaddleOCR), feeds it back into the pipeline.
4. **UPIDetector** — collect-request traps, fake payment proofs, QR/VPA risk.
5. **ImpersonationDetector** — bank/RBI/income-tax/courier/telecom impersonation.
6. **LLMDetector** — Claude-powered reasoning + recommendations (graceful template fallback).
7. **EnsembleDetector** — confidence-weighted fusion → final 0-100 score, risk level, category, reasons.

---

## Quick start

### Docker (recommended)
```bash
cp .env.example .env          # then edit SECRET_KEY
docker compose up --build     # API on http://localhost:8000
docker compose exec api python -m scripts.seed   # categories + admin user
```

### Local dev
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
export SECRET_KEY=dev-secret
# start Postgres + Redis (or `docker compose up db redis`)
alembic upgrade head
python -m scripts.seed
uvicorn app.main:app --reload
```

- Swagger UI: <http://localhost:8000/docs>
- ReDoc: <http://localhost:8000/redoc>
- Metrics: <http://localhost:8000/metrics>

### Tests
```bash
pytest                 # runs against in-memory SQLite, no services needed
pytest --cov=app
```

---

## API (v1)

| Method | Path | Auth | Purpose |
|---|---|---|---|
| POST | `/api/v1/auth/register` | — | Create account |
| POST | `/api/v1/auth/login` | — | Get access + refresh tokens |
| POST | `/api/v1/auth/refresh` | — | Rotate access token |
| POST | `/api/v1/detect/text` | ✅ | Detect scam in raw text/SMS/WhatsApp |
| POST | `/api/v1/detect/url` | ✅ | Detect malicious URL |
| POST | `/api/v1/detect/email` | ✅ | Detect phishing email |
| POST | `/api/v1/detect/upi` | ✅ | Detect UPI/payment fraud |
| POST | `/api/v1/detect/image` | ✅ | OCR + detect (screenshot/QR/UPI) |
| GET | `/api/v1/history` | ✅ | Paginated scan history |
| GET | `/api/v1/history/{scan_id}` | ✅ | Full scan detail |
| POST | `/api/v1/history/{scan_id}/feedback` | ✅ | Report correctness |
| GET | `/api/v1/admin/stats` | 🛡️ admin | Platform stats |
| GET | `/api/v1/admin/scam-trends` | 🛡️ admin | Trends & top categories |
| GET | `/health` `/ready` `/metrics` | — | Ops |

### Example: detect text
```bash
# 1. register + login
curl -s localhost:8000/api/v1/auth/register -H 'content-type: application/json' \
  -d '{"email":"u@x.com","password":"password123"}'
TOKEN=$(curl -s localhost:8000/api/v1/auth/login -H 'content-type: application/json' \
  -d '{"email":"u@x.com","password":"password123"}' | python -c 'import sys,json;print(json.load(sys.stdin)["access_token"])')

# 2. detect
curl -s localhost:8000/api/v1/detect/text \
  -H "authorization: Bearer $TOKEN" -H 'content-type: application/json' \
  -d '{"content":"URGENT: Your SBI KYC expired. Verify now http://bit.ly/x and share OTP or account blocked.","input_type":"SMS"}'
```

Response:
```json
{
  "scan_id": "f0e1...",
  "status": "COMPLETED",
  "input_type": "SMS",
  "scam_probability": 93,
  "risk_level": "SCAM",
  "confidence": 0.78,
  "category": "Bank Impersonation Scam",
  "reasons": ["Requests sensitive credentials (OTP/PIN/CVV)", "..."],
  "recommendation": "Do not click links or share information...",
  "risk_factors": [{"detector":"text","code":"text.credentials","description":"...","weight":0.36}],
  "engine_scores": [{"detector":"text","score":0.91,"confidence":0.7}],
  "model_version": "mvp-0.1.0",
  "created_at": "2026-06-27T..."
}
```

---

## Database schema
`users · scans · predictions · risk_factors · feedback · scam_categories`
— all with UUID PKs, `created_at/updated_at`, FKs with cascade rules, and
indexes on hot query paths (`scans(user_id, created_at)`, `predictions(risk_level)`, …).
Managed via Alembic (`alembic/versions/`).

## Roadmap seams (already wired)
- Voice / audio / real-time call engines → add `BaseDetector` subclass + registry entry.
- Browser extension → reuse `/detect/url` + `/detect/text`.
- Real models → `ENABLE_HEAVY_MODELS=true` + `requirements-ml.txt`.
- Active learning → `feedback` table feeds offline retraining + `rescore_batch` task.

## Directory layout
```
app/
  api/        routes (v1) + DI + health
  core/       config, logging, security, observability, exceptions
  db/         base, session, portable types
  models/     SQLAlchemy ORM models
  schemas/    Pydantic request/response contracts
  detectors/  engines + ensemble + registry
  services/   orchestration / use cases
  repositories/  data access
  workers/    Celery app + tasks
  utils/      helpers
  tests/      pytest suite
alembic/      migrations
scripts/      seed
deploy/       prometheus config
.github/      CI
```
