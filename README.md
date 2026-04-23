# Acme Logistics — Inbound Carrier Sales Agent

An AI voice agent that handles inbound carrier sales calls for a freight brokerage: verifies carriers against FMCSA, searches loads, negotiates rates up to 3 rounds, and books deals. Built on the HappyRobot platform for the FDE Technical Challenge.

## Live demo

| Resource | Link |
|---|---|
| **Live API** | https://happyrobot-carrier-sales-small-grass-4260.fly.dev |
| **API Docs (Swagger)** | https://happyrobot-carrier-sales-small-grass-4260.fly.dev/docs |
| **Dashboard** | https://carrier-call-insights.lovable.app |
| **HappyRobot Workflow** |https://platform.happyrobot.ai/fdehimanshusharma/workflows/aa508woutqet/editor/wpdq6y078kpn , https://platform.happyrobot.ai/deployments/aa508woutqet/gaku6z4marbl|
| **Loom Walkthrough** | https://www.loom.com/share/b66de4c6733a4a579ba8aa84217103a4 |

## Architecture
<img width="415" height="461" alt="image" src="https://github.com/user-attachments/assets/ecadcc72-8f2d-4858-bdaa-ee9e2423e02a" />




**Key design decision:** the LLM handles conversation; deterministic Python handles money. The negotiation engine is a pure function in `api/negotiation.py` with broker-configurable multipliers — not LLM-driven. This makes rate decisions auditable, unit-testable, and cheap to change.

## Tech stack

- **Voice agent:** HappyRobot platform (web call trigger)
- **Backend:** FastAPI, SQLAlchemy, SQLite (with Fly volume for persistence)
- **External APIs:** FMCSA QCMobile (carrier eligibility)
- **Deployment:** Docker → Fly.io with Let's Encrypt HTTPS
- **Dashboard:** Lovable (React + Recharts), reading from public metrics endpoints
- **Tests:** pytest (negotiation engine has 7 unit tests)

## Running locally

```bash
# 1. Setup
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # Windows; or `source .venv/bin/activate` on macOS/Linux
pip install -r requirements.txt

# 2. Configure secrets
cp .env.example .env
# Edit .env to add your FMCSA WebKey and a strong API_KEY

# 3. Run
uvicorn api.main:app --reload --port 8000

# 4. Test
pytest -v
```

API will be live at `http://localhost:8000`, Swagger at `http://localhost:8000/docs`.

## Running with Docker

```bash
docker compose up --build
```

## Deploying to Fly.io

```bash
fly launch --no-deploy           # one-time, creates fly.toml
fly volumes create carrier_data --region dfw --size 1
fly secrets set FMCSA_WEBKEY=xxx API_KEY=xxx
fly deploy
```

The Fly volume mounts at `/data` and persists SQLite across deploys.

## API endpoints

All endpoints (except `/health` and `/metrics/public/*`) require the `X-API-Key` header.

| Endpoint | Auth | Purpose |
|---|---|---|
| `GET /health` | ❌ | Liveness check |
| `POST /verify-carrier` | ✅ | FMCSA carrier eligibility |
| `POST /loads/search` | ✅ | Search loads by lane/equipment or load_id |
| `GET /loads/{load_id}` | ✅ | Direct load lookup |
| `POST /negotiate/evaluate` | ✅ | Evaluate carrier counter-offer |
| `POST /calls/events` | ✅ | Log call event from HappyRobot |
| `GET /metrics/summary` | ✅ | Aggregate metrics |
| `GET /metrics/calls` | ✅ | Recent calls list |
| `GET /metrics/public/summary` | ❌ | Read-only public summary (for dashboard) |
| `GET /metrics/public/calls` | ❌ | Read-only public calls list (for dashboard) |

The two `/metrics/public/*` endpoints are intentionally unauthenticated to support the dashboard without exposing the API key in client-side JavaScript. They expose only aggregate, non-sensitive data — no transcripts, no PII, no FMCSA credentials. All write operations and the negotiation engine remain key-protected.

## Negotiation engine

Lives in `api/negotiation.py`. Pure function, broker-configurable via `api/config.py`:

- `floor_multiplier: 0.92` — broker's walk-away floor
- `ceiling_multiplier: 1.08` — absolute max
- `proximity_accept_pct: 0.02` — auto-accept if carrier comes within 2% of our last counter

3 rounds maximum. Round 1 counters at 40% of the gap, round 2 at 65%, round 3 at 85%. Above-ceiling offers get countered at the ceiling on rounds 1–2, rejected on round 3. Unit-tested in `tests/test_negotiation.py`.

## Security

- HTTPS enforced via Fly.io's Let's Encrypt
- `X-API-Key` required on all write/operational endpoints
- FMCSA WebKey stored as Fly secret (never in code)
- API key stored as Fly secret + local `.env` (gitignored)
- Public metrics endpoints expose only aggregate, non-sensitive data

## What I'd build next

- Persistent storage swap from SQLite to Postgres for multi-tenant deployments
- Lane-level performance metrics (which origins/destinations book, which don't)
- Call duration and time-to-resolution tracking
- Webhook for booking confirmations into a real TMS (McLeod, MercuryGate)
- Backend-for-frontend proxy so the dashboard can hit auth'd endpoints without exposing the key

## License

MIT
