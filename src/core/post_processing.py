from typing import Any, Dict
from fastapi.responses import JSONResponse
from core.security import authorize
from config import settings
from core.authorization.whitelist import WhiteList


async def processing_login_response(data: Dict) -> Any:
    payload = data.get("data", {})
    content = await authorize.set_payload(payload).handle_login()

    if settings.TOKEN_VERIFY_BACKEND:
        whitelist_token = WhiteList(
            username=authorize.get_payload_by("username", ""), payload=content
        )

        await whitelist_token.set_expire(
            settings.ACCESS_TOKEN_EXPIRE_MINUTES
        ).store_access_token()

        await whitelist_token.set_expire(
            settings.REFRESH_TOKEN_EXPIRE_MINUTES
        ).store_refresh_token()

    response = JSONResponse(content=content)

    # TODO refactory set cookie
    response.set_cookie(
        key="refresh_token",
        value=content.get("refresh_token", ""),
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60,
    )

    return response
