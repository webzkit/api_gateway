import asyncio
from typing import Any, Dict
from fastapi.responses import JSONResponse
from config import settings
from core.helpers.cache import create_whitelist_token
from core.helpers.utils import hashkey
from core.security import authorize


expiration = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
expiration_refresh_token = settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60


# TODO
async def access_token_generate_handler(data: Dict) -> Any:
    payload = data.get("data", {})
    access_token = authorize.encrypt(payload)
    refresh_token = authorize.set_exprire(
        settings.REFRESH_TOKEN_EXPIRE_MINUTES
    ).encrypt(payload)

    content = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }

    username = data["data"]["username"]
    access_token_cache_key = (
        f"whitelist_token:{username}:access_token:{hashkey(access_token)}"
    )
    await create_whitelist_token(
        cache_key=access_token_cache_key, data=content, expiration=expiration
    )

    refresh_token_cache_key = (
        f"whitelist_token:{username}:refresh_token:{hashkey(refresh_token)}"
    )

    await create_whitelist_token(
        cache_key=refresh_token_cache_key,
        data=content,
        expiration=expiration_refresh_token,
    )

    response = JSONResponse(content=content)

    # TODO
    max_age = settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=max_age,
    )

    return response
