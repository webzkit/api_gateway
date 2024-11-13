from typing import Any, Dict
from fastapi.responses import JSONResponse
from core.security import encode_access_token
from config import settings


def access_token_generate_handler(data: Dict) -> Any:
    access_token = encode_access_token(data, settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token = encode_access_token(data, settings.REFRESH_TOKEN_EXPIRE_MINUTES)

    max_age = settings.REFRESH_TOKEN_EXPIRE_MINUTES * 60

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


def revoke_token(data: Dict) -> Any:
    print(data)
    return {"detail": "Logged out successfully"}
