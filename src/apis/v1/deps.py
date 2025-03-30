from typing import Annotated, Any, Dict
from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from schemas.rate_limit import sanitize_path
from core.helpers.rate_limit import is_rate_limited
from core.exceptions import RateLimitException
from config import settings
from core.monitors.logger import Logger
from core.security import authorize

auth_scheme = HTTPBearer()


DEFAULT_LIMIT = settings.REDIS_RATE_LIMIT_LIMIT
DEFAULT_PERIOD = settings.REDIS_RATE_LIMIT_PERIOD
SKIP_RATE_LIMIT_PATHS = ["health", "index"]

logger = Logger(__name__)


def use_author_for_dev(
    token: HTTPAuthorizationCredentials = Depends(auth_scheme),
) -> Any:
    return token.credentials


async def get_user(request: Request) -> Dict:
    try:
        return await authorize.set_token_bearer(
            request.headers.get("Authorization")
        ).user()
    except Exception as e:
        logger.debug(f"User not found - {e}")
        return {}


# TODO  make middleware
async def rate_limiter(
    request: Request, user: Annotated[dict, Depends(get_user)]
) -> None:
    path = sanitize_path(request.url.path) or "index"
    if path in SKIP_RATE_LIMIT_PATHS:
        return

    limit, period = DEFAULT_LIMIT, DEFAULT_PERIOD
    username = user.get("username", request.client.host)  # pyright: ignore

    is_limited = await is_rate_limited(
        user_id=username, path=path, limit=limit, period=period
    )

    if is_limited:
        logger.warning(f"Rate limit exceeded for user {username} on path {path}")
        raise RateLimitException("Rate limit exceeded.")
