from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.auth import require_api_key
from api.db import get_db
from api.models import Load
from api.schemas import LoadSummary, SearchLoadsRequest, SearchLoadsResponse

router = APIRouter(prefix="/loads", tags=["loads"])


@router.post("/search", response_model=SearchLoadsResponse, dependencies=[Depends(require_api_key)])
async def search_loads(
    payload: SearchLoadsRequest,
    db: Session = Depends(get_db),
) -> SearchLoadsResponse:
    q = db.query(Load)
    if payload.origin:
        q = q.filter(Load.origin.ilike(f"%{payload.origin}%"))
    if payload.destination:
        q = q.filter(Load.destination.ilike(f"%{payload.destination}%"))
    if payload.equipment_type:
        q = q.filter(Load.equipment_type == payload.equipment_type.lower())
    q = q.order_by(Load.pickup_datetime.asc()).limit(5)

    results = [LoadSummary.model_validate(l, from_attributes=True) for l in q.all()]
    return SearchLoadsResponse(loads=results, count=len(results))


@router.get("/{load_id}", response_model=LoadSummary, dependencies=[Depends(require_api_key)])
async def get_load(load_id: str, db: Session = Depends(get_db)) -> LoadSummary:
    load = db.query(Load).filter(Load.load_id == load_id).first()
    if not load:
        raise HTTPException(status_code=404, detail=f"Load {load_id} not found")
    return LoadSummary.model_validate(load, from_attributes=True)