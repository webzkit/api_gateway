from typing import Annotated, Any
from core.route import route
from fastapi import APIRouter, Body, status, Request, Response
from config import settings
from schemas.user_service.user import LoginRequest, RefreshTokenRequest
from core.exception.http_exception import UnauthorizedException
from core.exception.auth_exception import (
    AuthTokenCorrupted,
    AuthTokenMissing,
    AuthTokenExpired,
)
from core.security import authorize

router = APIRouter()


SERVICE_NAME = settings.ENGINE_SERVICE_NAME


@route(
    request_method=router.post,
    path="/login",
    status_code=status.HTTP_200_OK,
    payload_key="login_form",
    service_name=SERVICE_NAME,
    authentication_required=False,
    post_processing_func="core.post_processing.processing_login_response",
    response_model="schemas.user_service.user.LoginResponse",
)
async def login(
    login_form: Annotated[LoginRequest, Body()], request: Request, response: Response
):
    pass


@router.post("/refresh", status_code=status.HTTP_200_OK)
async def refresh(
    token: Annotated[RefreshTokenRequest, Body()], request: Request, response: Response
) -> Any:
    try:
        return await authorize.set_token(token=token.token).handle_refresh()
    except (AuthTokenMissing, AuthTokenExpired, AuthTokenCorrupted, Exception) as e:
        raise UnauthorizedException(str(e))
