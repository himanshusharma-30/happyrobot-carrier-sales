"""Pydantic request/response schemas — the public API contract."""
from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field


# ---------- verify_carrier ----------
class VerifyCarrierRequest(BaseModel):
    mc_number: str = Field(..., description="Motor Carrier number, digits only")


class VerifyCarrierResponse(BaseModel):
    eligible: bool
    carrier_name: Optional[str] = None
    dot_number: Optional[str] = None
    mc_number: str
    reason: Optional[str] = None


# ---------- search_loads ----------
class SearchLoadsRequest(BaseModel):
    load_id: Optional[str] = None          # NEW
    origin: Optional[str] = None
    destination: Optional[str] = None
    equipment_type: Optional[str] = None
    pickup_date: Optional[str] = None


class LoadSummary(BaseModel):
    load_id: str
    origin: str
    destination: str
    pickup_datetime: datetime
    delivery_datetime: datetime
    equipment_type: str
    loadboard_rate: float
    miles: Optional[int] = None
    weight: Optional[int] = None
    commodity_type: Optional[str] = None
    num_of_pieces: Optional[int] = None
    dimensions: Optional[str] = None
    notes: Optional[str] = None


class SearchLoadsResponse(BaseModel):
    loads: list[LoadSummary]
    count: int


# ---------- evaluate_offer ----------
class EvaluateOfferRequest(BaseModel):
    call_id: str = Field(..., description="HappyRobot call ID — scopes negotiation state")
    load_id: str
    carrier_offer: float


class EvaluateOfferResponse(BaseModel):
    action: Literal["accept", "counter", "reject"]
    round_number: int
    agreed_rate: Optional[float] = None
    counter_offer: Optional[float] = None
    message: str


# ---------- calls/events ----------
class CallEventRequest(BaseModel):
    call_id: str
    mc_number: Optional[str] = None
    carrier_name: Optional[str] = None
    load_id: Optional[str] = None
    loadboard_rate: Optional[float] = None
    final_rate: Optional[float] = None
    num_negotiation_rounds: int = 0
    outcome: str
    sentiment: str
    transcript: Optional[str] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None


class CallEventResponse(BaseModel):
    call_id: str
    stored: bool


# ---------- metrics ----------
class MetricsSummary(BaseModel):
    total_calls: int
    calls_today: int
    booking_rate: float  # 0–1
    avg_negotiation_rounds: float
    avg_rate_delta_pct: float  # avg (final - loadboard) / loadboard
    outcome_breakdown: dict[str, int]
    sentiment_breakdown: dict[str, int]


class CallListItem(BaseModel):
    call_id: str
    mc_number: Optional[str]
    carrier_name: Optional[str]
    load_id: Optional[str]
    loadboard_rate: Optional[float]
    final_rate: Optional[float]
    num_negotiation_rounds: int
    outcome: Optional[str]
    sentiment: Optional[str]
    created_at: datetime