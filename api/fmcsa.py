"""Thin client for the FMCSA QCMobile API, with in-memory caching."""
import time
from typing import Optional

import httpx

from api.config import settings

BASE_URL = "https://mobile.fmcsa.dot.gov/qc/services"
_cache: dict[str, tuple[float, dict]] = {}  # mc -> (expires_at, payload)


async def lookup_carrier_by_mc(mc_number: str) -> Optional[dict]:
    """Return parsed carrier details or None if not found.

    Returned shape:
    {
      "legal_name": str,
      "dot_number": str,
      "allowed_to_operate": "Y" | "N",
      "status_code": "A" | "I" | ...,
      "oos_date": str | None,
    }
    """
    mc = mc_number.strip().lstrip("MCmc ").lstrip()

    # Cache hit?
    if mc in _cache and _cache[mc][0] > time.time():
        return _cache[mc][1]

    url = f"{BASE_URL}/carriers/docket-number/{mc}"
    params = {"webKey": settings.fmcsa_webkey}

    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(url, params=params)

    if resp.status_code != 200:
        return None

    data = resp.json()
    content = data.get("content")
    if not content:
        return None

    # FMCSA may return a list or a dict depending on how many carriers match
    first = content[0] if isinstance(content, list) else content
    carrier = first.get("carrier", {})

    parsed = {
        "legal_name": carrier.get("legalName"),
        "dot_number": str(carrier.get("dotNumber") or ""),
        "allowed_to_operate": carrier.get("allowedToOperate"),
        "status_code": carrier.get("statusCode"),
        "oos_date": carrier.get("oosDate"),
    }

    _cache[mc] = (time.time() + settings.fmcsa_cache_ttl_seconds, parsed)
    return parsed


def evaluate_eligibility(carrier: dict) -> tuple[bool, Optional[str]]:
    """Apply broker's eligibility rules. Returns (eligible, reason_if_not)."""
    if carrier.get("allowed_to_operate") != "Y":
        return False, "Carrier is not currently authorized to operate"
    if carrier.get("status_code") != "A":
        return False, "Carrier status is not active"
    if carrier.get("oos_date"):
        return False, f"Carrier is out of service (as of {carrier['oos_date']})"
    return True, None