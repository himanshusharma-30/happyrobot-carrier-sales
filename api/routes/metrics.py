from datetime import date, datetime
from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from api.auth import require_api_key
from api.db import get_db
from api.models import CallEvent
from api.schemas import CallListItem, MetricsSummary

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("/summary", response_model=MetricsSummary, dependencies=[Depends(require_api_key)])
async def metrics_summary(db: Session = Depends(get_db)) -> MetricsSummary:
    all_calls = db.query(CallEvent).all()
    total = len(all_calls)

    today = date.today()
    calls_today = sum(1 for c in all_calls if c.created_at and c.created_at.date() == today)

    booked = [c for c in all_calls if c.outcome == "booked"]
    booking_rate = (len(booked) / total) if total else 0.0

    rounds_sample = [c.num_negotiation_rounds for c in all_calls if c.num_negotiation_rounds]
    avg_rounds = (sum(rounds_sample) / len(rounds_sample)) if rounds_sample else 0.0

    deltas = [
        (c.final_rate - c.loadboard_rate) / c.loadboard_rate
        for c in booked
        if c.final_rate and c.loadboard_rate
    ]
    avg_delta = (sum(deltas) / len(deltas)) if deltas else 0.0

    outcome_counts: dict[str, int] = {}
    for c in all_calls:
        if c.outcome:
            outcome_counts[c.outcome] = outcome_counts.get(c.outcome, 0) + 1

    sentiment_counts: dict[str, int] = {}
    for c in all_calls:
        if c.sentiment:
            sentiment_counts[c.sentiment] = sentiment_counts.get(c.sentiment, 0) + 1

    return MetricsSummary(
        total_calls=total,
        calls_today=calls_today,
        booking_rate=round(booking_rate, 4),
        avg_negotiation_rounds=round(avg_rounds, 2),
        avg_rate_delta_pct=round(avg_delta, 4),
        outcome_breakdown=outcome_counts,
        sentiment_breakdown=sentiment_counts,
    )


@router.get("/calls", response_model=list[CallListItem], dependencies=[Depends(require_api_key)])
async def list_calls(
    limit: int = 50,
    db: Session = Depends(get_db),
) -> list[CallListItem]:
    rows = (
        db.query(CallEvent)
        .order_by(CallEvent.created_at.desc())
        .limit(limit)
        .all()
    )
    return [CallListItem.model_validate(r, from_attributes=True) for r in rows]