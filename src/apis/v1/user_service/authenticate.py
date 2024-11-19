from typing import Annotated, Any

from fastapi.responses import JSONResponse
from core.route import route
from fastapi import APIRouter, Body, HTTPException, status, Request, Response
from config import settings
from schemas.user_service.user import LoginForm
from core.security import decode_access_token
from core.exception.http_exception import UnauthorizedException
from core.exceptions import AuthTokenCorrupted, AuthTokenMissing
from core.helpers.cache import revoke_whitelist_token
from core.post_processing import access_token_generate_handler
from core.helpers.utils import hashkey


router = APIRouter()


@route(
    request_method=router.post,
    path="/login",
    status_code=status.HTTP_200_OK,
    payload_key="login_form",
    service_url=settings.USER_SERVICE_URL,
    authentication_required=False,
    post_processing_func="core.post_processing.access_token_generate_handler",
    response_model="schemas.user_service.user.LoginResponse",
)
async def login(
    login_form: Annotated[LoginForm, Body()], request: Request, response: Response
):
    pass


@router.post("/refresh", status_code=status.HTTP_200_OK)
async def refresh(request: Request, response: Response) -> Any:
    refresh_token = request.cookies.get("refresh_token")
    try:
        user = await decode_access_token(
            authorization=refresh_token, use_for="refresh_token"
        )

        payload = {"data": user.get("payload")}

        return await access_token_generate_handler(payload)

    except Exception as e:
        raise UnauthorizedException(str(e))


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(request: Request, response: Response) -> Any:
    token = request.headers.get("authorization")

    # only use cookie
    # TODO
    refresh_token = request.cookies.get("refresh_token")

    try:
        payload = await decode_access_token(token)
        username = payload["payload"]["username"]

        cache_key = f"whitelist_token:{username}:access_token:{hashkey(str(token).replace('Bearer ', ''))}"
        refresh_cache_key = (
            f"whitelist_token:{username}:refresh_token:{hashkey(str(refresh_token))}"
        )

        await revoke_whitelist_token(cache_key)
        await revoke_whitelist_token(refresh_cache_key)

        response = JSONResponse(content={"detail": "Logged out successfully"})

        # Remove cookie
        response.delete_cookie(key="refresh_token")

        return response
    except (AuthTokenMissing, AuthTokenMissing, AuthTokenCorrupted) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=e,
            headers={"WWW-Authenticate": "Bearer"},
        )
