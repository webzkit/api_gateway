from typing import Any, Dict
from fastapi.responses import JSONResponse
from core.security import encode_access_token
from config import settings
from core.helpers.cache import create_whitelist_token

expiration = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60


@create_whitelist_token(key_prefix="whitelist_token", expiration=expiration)
async def access_token_generate_handler(data: Dict) -> Any:
    access_token = encode_access_token(data, settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token = encode_access_token(data, settings.REFRESH_TOKEN_EXPIRE_MINUTES)

    max_age = settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60 * 60

    response = JSONResponse(
        content={
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=max_age,
    )

    return response
