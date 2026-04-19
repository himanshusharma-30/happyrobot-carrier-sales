from fastapi import APIRouter, Depends

from api.auth import require_api_key
from api.fmcsa import evaluate_eligibility, lookup_carrier_by_mc
from api.schemas import VerifyCarrierRequest, VerifyCarrierResponse

router = APIRouter(prefix="/verify-carrier", tags=["carrier"])


@router.post("", response_model=VerifyCarrierResponse, dependencies=[Depends(require_api_key)])
async def verify_carrier(payload: VerifyCarrierRequest) -> VerifyCarrierResponse:
    carrier = await lookup_carrier_by_mc(payload.mc_number)
    if not carrier:
        return VerifyCarrierResponse(
            eligible=False,
            mc_number=payload.mc_number,
            reason="MC number not found in FMCSA records",
        )

    eligible, reason = evaluate_eligibility(carrier)
    return VerifyCarrierResponse(
        eligible=eligible,
        mc_number=payload.mc_number,
        carrier_name=carrier.get("legal_name"),
        dot_number=carrier.get("dot_number"),
        reason=reason,
    )