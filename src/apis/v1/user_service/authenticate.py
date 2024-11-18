from typing import Annotated, Any

from fastapi.responses import JSONResponse
from core.route import route
from fastapi import APIRouter, Body, Depends, HTTPException, status, Request, Response
from config import settings
from schemas.user_service.user import LoginForm
from apis.v1.deps import is_supper_admin
from core.security import decode_access_token
from core.exception.http_exception import UnauthorizedException
from core.security import encode_access_token
from core.exceptions import AuthTokenCorrupted, AuthTokenMissing
from core.helpers.cache import revoke_whitelist_token


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
        user = await decode_access_token(refresh_token)
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


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(request: Request, response: Response) -> Any:
    token = request.headers.get("authorization")
    exc = None

    try:
        payload = await decode_access_token(token)
        username = payload['payload']['username']

        cache_key = f"whitelist_token:{username}:{str(token).replace('Bearer ', '')}"
        await revoke_whitelist_token(cache_key)
        response = JSONResponse(
            content={
                "detail": "Logged out successfully"
            }
        )

        return response
    except (AuthTokenMissing, AuthTokenMissing, AuthTokenCorrupted)as e:
        exc = str(e)
    except Exception as e:
        exc = str(e)
    finally:
        if exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=exc,
                headers={"WWW-Authenticate": "Bearer"},
            )

