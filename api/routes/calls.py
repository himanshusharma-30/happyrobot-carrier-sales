from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from api.auth import require_api_key
from api.db import get_db
from api.models import CallEvent
from api.schemas import CallEventRequest, CallEventResponse

router = APIRouter(prefix="/calls", tags=["calls"])


@router.post("/events", response_model=CallEventResponse, dependencies=[Depends(require_api_key)])
async def ingest_call_event(
    payload: CallEventRequest,
    db: Session = Depends(get_db),
) -> CallEventResponse:
    existing = db.query(CallEvent).filter(CallEvent.call_id == payload.call_id).first()
    if existing:
        # Idempotent: update, don't duplicate
        for k, v in payload.model_dump(exclude_unset=True).items():
            setattr(existing, k, v)
    else:
        db.add(CallEvent(**payload.model_dump()))
    db.commit()
    return CallEventResponse(call_id=payload.call_id, stored=True)