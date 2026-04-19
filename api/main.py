"""FastAPI app entrypoint."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.db import Base, engine
from api.routes import calls, carrier, loads, metrics, negotiate
from api.seed import seed_loads_from_json


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on boot + seed loads if empty
    Base.metadata.create_all(bind=engine)
    seed_loads_from_json("loads.json")
    yield


app = FastAPI(
    title="Acme Logistics Carrier Sales API",
    version="0.1.0",
    description="Backend for the HappyRobot inbound carrier sales agent.",
    lifespan=lifespan,
)

# CORS for the dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later for prod
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok"}


app.include_router(carrier.router)
app.include_router(loads.router)
app.include_router(negotiate.router)
app.include_router(calls.router)
app.include_router(metrics.router)