from typing import Annotated, Any
from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from schemas.rate_limit import sanitize_path
from core.helpers.rate_limit import is_rate_limited
from core.exceptions import RateLimitException
from config import settings


auth_scheme = HTTPBearer()


DEFAULT_LIMIT = settings.REDIS_RATE_LIMIT_LIMIT
DEFAULT_PERIOD = settings.REDIS_RATE_LIMIT_PERIOD


def is_supper_admin(token: HTTPAuthorizationCredentials = Depends(auth_scheme)) -> Any:
    return token.credentials


async def get_option_user(request: Request) -> Any:
    token = request.headers.get("Authorization")
    if not token:
        return None
    return {"id": 1}


async def rate_limiter(
    request: Request, user: Annotated[dict, Depends(get_option_user)]
) -> None:
    path = sanitize_path(request.url.path)
    limit, period = DEFAULT_LIMIT, DEFAULT_PERIOD
    user_id = request.client.host  # pyright: ignore

    if user:
        user_id = user["id"]

    is_limited = await is_rate_limited(
        user_id=user_id, path=path, limit=limit, period=period
    )

    if is_limited:
        raise RateLimitException("Rate limit exceeded.")
