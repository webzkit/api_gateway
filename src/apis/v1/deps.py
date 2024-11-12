from typing import Any
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


async def rate_limiter(
    request: Request,
) -> None:
    path = sanitize_path(request.url.path)
    user_id = request.client.host
    limit, period = DEFAULT_LIMIT, DEFAULT_PERIOD

    is_limited = await is_rate_limited(
        user_id=user_id, path=path, limit=limit, period=period
    )
    if is_limited:
        raise RateLimitException("Rate limit exceeded.")
