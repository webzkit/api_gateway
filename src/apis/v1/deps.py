from typing import Annotated, Any
from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from schemas.rate_limit import sanitize_path
from core.helpers.rate_limit import is_rate_limited
from core.exceptions import RateLimitException
from config import settings
from core.security import get_current_user_by
from core.logger import Logger


auth_scheme = HTTPBearer()


DEFAULT_LIMIT = settings.REDIS_RATE_LIMIT_LIMIT
DEFAULT_PERIOD = settings.REDIS_RATE_LIMIT_PERIOD
SKIP_RATE_LIMIT_PATHS = ["health", "index"]

logger = Logger(__name__)


def use_author_for_dev(
    token: HTTPAuthorizationCredentials = Depends(auth_scheme),
) -> Any:
    return token.credentials


async def get_option_user(request: Request) -> Any:
    user_at = await get_current_user_by(request.headers.get("Authorization"))
    if user_at is None:
        return {"username": request.client.host}  # pyright: ignore

    return user_at


async def rate_limiter(
    request: Request, user: Annotated[dict, Depends(get_option_user)]
) -> None:
    path = sanitize_path(request.url.path) or "index"
    if path in SKIP_RATE_LIMIT_PATHS:
        return

    limit, period = DEFAULT_LIMIT, DEFAULT_PERIOD
    user_id = user["username"] or request.client.host  # pyright: ignore

    is_limited = await is_rate_limited(
        user_id=user_id, path=path, limit=limit, period=period
    )

    if is_limited:
        logger.warning(f"Rate limit exceeded for user {user_id} on path {path}")
        raise RateLimitException("Rate limit exceeded.")
