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

router = APIRouter()


@router.get("/info", status_code=status.HTTP_200_OK)
async def me(request: Request, response: Response) -> Any:
    try:
        return JSONResponse(content={"detail": "Show me"})
    except (AuthTokenMissing, AuthTokenExpired, AuthTokenCorrupted) as e:
        raise UnauthorizedException(str(e))


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
