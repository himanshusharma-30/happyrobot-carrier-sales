from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.auth import require_api_key
from api.db import get_db
from api.models import Load, NegotiationState
from api.negotiation import MAX_ROUNDS, evaluate
from api.schemas import EvaluateOfferRequest, EvaluateOfferResponse

router = APIRouter(prefix="/negotiate", tags=["negotiate"])


@router.post("/evaluate", response_model=EvaluateOfferResponse, dependencies=[Depends(require_api_key)])
async def evaluate_offer(
    payload: EvaluateOfferRequest,
    db: Session = Depends(get_db),
) -> EvaluateOfferResponse:
    load = db.query(Load).filter(Load.load_id == payload.load_id).first()
    if not load:
        raise HTTPException(status_code=404, detail=f"Load {payload.load_id} not found")

    # Fetch or create per-call negotiation state
    state = db.query(NegotiationState).filter(NegotiationState.call_id == payload.call_id).first()
    if state is None:
        state = NegotiationState(call_id=payload.call_id, load_id=payload.load_id, round_number=0)
        db.add(state)
        db.flush()

    next_round = state.round_number + 1

    decision = evaluate(
        loadboard_rate=load.loadboard_rate,
        carrier_offer=payload.carrier_offer,
        round_number=next_round,
        last_counter=state.last_counter,
    )

    # Persist state for the next round
    state.round_number = next_round
    state.last_carrier_offer = payload.carrier_offer
    if decision.counter_offer is not None:
        state.last_counter = decision.counter_offer
    db.commit()

    return EvaluateOfferResponse(
        action=decision.action,
        round_number=decision.round_number,
        agreed_rate=decision.agreed_rate,
        counter_offer=decision.counter_offer,
        message=decision.message,
    )