from typing import Any
from fastapi.responses import JSONResponse
from fastapi import APIRouter, status, Request, Response
from core.exception.http_exception import UnauthorizedException
from core.exception.auth_exception import (
    AuthTokenCorrupted,
    AuthTokenMissing,
    AuthTokenExpired,
)
from core.security import authorize
from config import settings
from core.route import route

router = APIRouter()


SERVICE_NAME = settings.ENGINE_SERVICE_NAME


@route(
    request_method=router.get,
    path="",
    status_code=status.HTTP_200_OK,
    payload_key=None,
    service_name=SERVICE_NAME,
    authentication_required=True,
    post_processing_func=None,
    response_list=False,
)
async def me(request: Request, response: Response) -> Any:
    pass


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(request: Request, response: Response) -> Any:
    try:
        token = request.headers.get("authorization", "")
        await authorize.handle_logout(token=token)

        return JSONResponse(content={"detail": "Logged out successfully"})

        # Destroy cookie
        # response.delete_cookie(key="refresh_token")
    except (AuthTokenMissing, AuthTokenExpired, AuthTokenCorrupted) as e:
        raise UnauthorizedException(str(e))
