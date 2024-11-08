from typing import Any, Dict
from core.security import encode_access_token
from config import settings


def access_token_generate_handler(data: Dict) -> Any:
    access_token = encode_access_token(data, settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token = encode_access_token(data, settings.REFRESH_TOKEN_EXPIRE_MINUTES)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }
