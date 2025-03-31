from typing import Annotated, Any
from fastapi.responses import JSONResponse
from core.route import route
from fastapi import APIRouter, Body, status, Request, Response
from config import settings
from schemas.user_service.user import LoginForm
from core.exception.http_exception import UnauthorizedException
from core.exceptions import AuthTokenCorrupted, AuthTokenMissing, AuthTokenExpired
from core.post_processing import processing_login_response
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
    login_form: Annotated[LoginForm, Body()], request: Request, response: Response
):
    pass


@router.post("/refresh", status_code=status.HTTP_200_OK)
async def refresh(request: Request, response: Response) -> Any:
    try:
        refresh_token = request.cookies.get("refresh_token")
        return await authorize.handle_refresh(token=refresh_token)
    except (AuthTokenMissing, AuthTokenExpired, AuthTokenCorrupted, Exception) as e:
        raise UnauthorizedException(str(e))


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(request: Request, response: Response) -> Any:
    try:
        token = request.headers.get("authorization")
        await authorize.handle_logout(token)
        return JSONResponse(content={"detail": "Logged out successfully"})

        # Destroy cookie
        # response.delete_cookie(key="refresh_token")
    except (AuthTokenMissing, AuthTokenExpired, AuthTokenCorrupted) as e:
        raise UnauthorizedException(str(e))
