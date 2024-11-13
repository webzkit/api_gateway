from typing import Annotated, Any
from core.route import route
from fastapi import APIRouter, Body, Depends, status, Request, Response
from config import settings
from schemas.user_service.user import LoginForm
from apis.v1.deps import is_supper_admin
from core.security import decode_access_token
from core.exception.http_exception import UnauthorizedException
from core.security import encode_access_token


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
        user = decode_access_token(refresh_token)
        payload = {"data": user.get("payload")}
        access_token = encode_access_token(
            payload, settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        refresh_token = encode_access_token(
            payload, settings.REFRESH_TOKEN_EXPIRE_MINUTES
        )
        max_age = settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=max_age,
        )
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    except Exception as e:
        raise UnauthorizedException(str(e))


@route(
    request_method=router.post,
    path="/logout",
    status_code=status.HTTP_200_OK,
    payload_key=None,
    service_url=settings.USER_SERVICE_URL,
    authentication_required=True,
    post_processing_func="core.post_processing.revoke_token",
    authentication_token_decoder="core.security.decode_access_token",
    service_header_generator="core.security.generate_request_header",
)
async def logout(request: Request, response: Response, token=Depends(is_supper_admin)):
    pass
