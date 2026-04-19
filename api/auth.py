"""Simple header-based API key auth for all protected routes.

Uses APIKeyHeader so the scheme shows up in /docs with an Authorize button.
"""
from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

from api.config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def require_api_key(api_key: str = Security(api_key_header)):
    if api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )